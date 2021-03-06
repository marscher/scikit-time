import unittest
import numpy as np

from sktime.covariance.online_covariance import OnlineCovariance

__author__ = 'noe'

np.random.seed(123)

data = np.random.rand(5000, 2)
weights = np.random.randn(len(data))
mean_const = np.random.rand(2)


class TestCovarEstimator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.lag = 10
        cls.data = data
        cls.X = cls.data[:-cls.lag, :]
        cls.Y = cls.data[cls.lag:, :]
        cls.T = cls.X.shape[0]

        # Chunk size:
        cls.L = 1000
        # Number of chunks:
        cls.nchunks = 10

        # Weights:
        class weight_object(object):
            def __init__(self):
                self.A = np.random.rand(2)

            def weights(self, X):
                return np.dot(X, self.A)

        cls.wobj = weight_object()
        # Constant mean to be removed:
        cls.mean_const = mean_const
        # Chunksize:
        cls.chunksize = 500
        # column subsets
        cls.cols_2 = np.array([0])

        # moments of X and Y
        cls.w = np.shape(cls.X)[0]
        cls.w_lag0 = np.shape(cls.data)[0]
        cls.wsym = 2 * np.shape(cls.X)[0]
        cls.wsym_lag0 = 2 * np.shape(cls.data)[0]
        cls.sx = cls.X.sum(axis=0)
        cls.sy = cls.Y.sum(axis=0)
        cls.sx_lag0 = cls.data.sum(axis=0)
        cls.Mxx = (1.0 / cls.w) * np.dot(cls.X.T, cls.X)
        cls.Mxx_lag0 = (1.0 / cls.w_lag0) * np.dot(cls.data.T, cls.data)
        cls.Mxy = (1.0 / cls.w) * np.dot(cls.X.T, cls.Y)
        cls.mx = cls.sx / float(cls.w)
        cls.mx_lag0 = cls.sx_lag0 / float(cls.w_lag0)
        cls.my = cls.sy / float(cls.w)
        cls.X0 = cls.X - cls.mx
        cls.X0_lag0 = cls.data - cls.mx_lag0
        cls.Y0 = cls.Y - cls.my
        cls.Mxx0 = (1.0 / cls.w) * np.dot(cls.X0.T, cls.X0)
        cls.Mxx0_lag0 = (1.0 / cls.w_lag0) * np.dot(cls.X0_lag0.T, cls.X0_lag0)
        cls.Mxy0 = (1.0 / cls.w) * np.dot(cls.X0.T, cls.Y0)

        # moments of x and y, constant mean:
        cls.Xc = cls.X - cls.mean_const
        cls.Xc_lag0 = cls.data - cls.mean_const
        cls.Yc = cls.Y - cls.mean_const
        cls.sx_c = np.sum(cls.Xc, axis=0)
        cls.sx_c_lag0 = np.sum(cls.Xc_lag0, axis=0)
        cls.sy_c = np.sum(cls.Yc, axis=0)
        cls.mx_c = cls.sx_c / float(cls.w)
        cls.mx_c_lag0 = cls.sx_c_lag0 / float(cls.w_lag0)
        cls.my_c = cls.sy_c / float(cls.w)
        cls.Mxx_c = (1.0 / cls.w) * np.dot(cls.Xc.T, cls.Xc)
        cls.Mxx_c_lag0 = (1.0 / cls.w_lag0) * np.dot(cls.Xc_lag0.T, cls.Xc_lag0)
        cls.Mxy_c = (1.0 / cls.w) * np.dot(cls.Xc.T, cls.Yc)

        # symmetric moments
        cls.s_sym = cls.sx + cls.sy
        cls.Mxx_sym = (1.0 / cls.wsym) * (np.dot(cls.X.T, cls.X) + np.dot(cls.Y.T, cls.Y))
        cls.Mxy_sym = (1.0 / cls.wsym) * (np.dot(cls.X.T, cls.Y) + np.dot(cls.Y.T, cls.X))
        cls.m_sym = cls.s_sym / float(cls.wsym)
        cls.X0_sym = cls.X - cls.m_sym
        cls.Y0_sym = cls.Y - cls.m_sym
        cls.Mxx0_sym = (1.0 / cls.wsym) * (np.dot(cls.X0_sym.T, cls.X0_sym) + np.dot(cls.Y0_sym.T, cls.Y0_sym))
        cls.Mxy0_sym = (1.0 / cls.wsym) * (np.dot(cls.X0_sym.T, cls.Y0_sym) + np.dot(cls.Y0_sym.T, cls.X0_sym))

        # symmetric moments, constant mean
        cls.s_c_sym = cls.sx_c + cls.sy_c
        cls.m_c_sym = cls.s_c_sym / float(cls.wsym)
        cls.Mxx_c_sym = (1.0 / cls.wsym) * (np.dot(cls.Xc.T, cls.Xc) + np.dot(cls.Yc.T, cls.Yc))
        cls.Mxy_c_sym = (1.0 / cls.wsym) * (np.dot(cls.Xc.T, cls.Yc) + np.dot(cls.Yc.T, cls.Xc))

        # weighted moments, object case:
        cls.X_weights = cls.wobj.weights(cls.X)
        cls.X_weighted = cls.X_weights[:, np.newaxis] * cls.X
        cls.data_weights = cls.wobj.weights(cls.data)
        cls.data_weights_lagged = cls.data_weights[:-cls.lag]
        cls.data_weighted = cls.data_weights[:, np.newaxis] * cls.data
        cls.wesum_obj = np.sum(cls.X_weights)
        cls.wesum_obj_sym = 2 * np.sum(cls.X_weights)
        cls.wesum_obj_lag0 = np.sum(cls.data_weights)
        cls.sx_wobj = (cls.X_weights[:, None] * cls.X).sum(axis=0)
        cls.sx_wobj_lag0 = (cls.data_weights[:, None] * cls.data).sum(axis=0)
        cls.sy_wobj = (cls.X_weights[:, None] * cls.Y).sum(axis=0)
        cls.Mxx_wobj = (1.0 / cls.wesum_obj) * np.dot((cls.X_weights[:, None] * cls.X).T, cls.X)
        cls.Mxx_wobj_lag0 = (1.0 / cls.wesum_obj_lag0) * np.dot((cls.data_weights[:, None] * cls.data).T, cls.data)
        cls.Mxy_wobj = (1.0 / cls.wesum_obj) * np.dot((cls.X_weights[:, None] * cls.X).T, cls.Y)
        cls.mx_wobj = cls.sx_wobj / float(cls.wesum_obj)
        cls.mx_wobj_lag0 = cls.sx_wobj_lag0 / float(cls.wesum_obj_lag0)
        cls.my_wobj = cls.sy_wobj / float(cls.wesum_obj)
        cls.X0_wobj = cls.X - cls.mx_wobj
        cls.X0_wobj_lag0 = cls.data - cls.mx_wobj_lag0
        cls.Y0_wobj = cls.Y - cls.my_wobj
        cls.Mxx0_wobj = (1.0 / cls.wesum_obj) * np.dot((cls.X_weights[:, None] * cls.X0_wobj).T, cls.X0_wobj)
        cls.Mxx0_wobj_lag0 = (1.0 / cls.wesum_obj_lag0) * np.dot((cls.data_weights[:, None] * cls.X0_wobj_lag0).T
                                                                 , cls.X0_wobj_lag0)
        cls.Mxy0_wobj = (1.0 / cls.wesum_obj) * np.dot((cls.X_weights[:, None] * cls.X0_wobj).T, cls.Y0_wobj)

        # weighted symmetric moments, object case:
        cls.s_sym_wobj = cls.sx_wobj + cls.sy_wobj
        cls.Mxx_sym_wobj = (1.0 / cls.wesum_obj_sym) * (np.dot((cls.X_weights[:, None] * cls.X).T, cls.X)
                                                        + np.dot((cls.X_weights[:, None] * cls.Y).T, cls.Y))
        cls.Mxy_sym_wobj = (1.0 / cls.wesum_obj_sym) * (np.dot((cls.X_weights[:, None] * cls.X).T, cls.Y)
                                                        + np.dot((cls.X_weights[:, None] * cls.Y).T, cls.X))
        cls.m_sym_wobj = cls.s_sym_wobj / float(2 * cls.wesum_obj)
        cls.X0_sym_wobj = cls.X - cls.m_sym_wobj
        cls.Y0_sym_wobj = cls.Y - cls.m_sym_wobj
        cls.Mxx0_sym_wobj = (1.0 / cls.wesum_obj_sym) * (
                    np.dot((cls.X_weights[:, None] * cls.X0_sym_wobj).T, cls.X0_sym_wobj)
                    + np.dot((cls.X_weights[:, None] * cls.Y0_sym_wobj).T, cls.Y0_sym_wobj))
        cls.Mxy0_sym_wobj = (1.0 / cls.wesum_obj_sym) * (
                    np.dot((cls.X_weights[:, None] * cls.X0_sym_wobj).T, cls.Y0_sym_wobj)
                    + np.dot((cls.X_weights[:, None] * cls.Y0_sym_wobj).T, cls.X0_sym_wobj))

        # weighted moments, object case, constant mean
        cls.sx_c_wobj = (cls.X_weights[:, None] * cls.Xc).sum(axis=0)
        cls.sx_c_wobj_lag0 = (cls.data_weights[:, None] * cls.Xc_lag0).sum(axis=0)
        cls.sy_c_wobj = (cls.X_weights[:, None] * cls.Yc).sum(axis=0)
        cls.Mxx_c_wobj = (1.0 / cls.wesum_obj) * np.dot((cls.X_weights[:, None] * cls.Xc).T, cls.Xc)
        cls.Mxx_c_wobj_lag0 = (1.0 / cls.wesum_obj_lag0) * np.dot((cls.data_weights[:, None] * cls.Xc_lag0).T,
                                                                  cls.Xc_lag0)
        cls.Mxy_c_wobj = (1.0 / cls.wesum_obj) * np.dot((cls.X_weights[:, None] * cls.Xc).T, cls.Yc)
        cls.mx_c_wobj = cls.sx_c_wobj / float(cls.wesum_obj)
        cls.mx_c_wobj_lag0 = cls.sx_c_wobj_lag0 / float(cls.wesum_obj_lag0)
        cls.my_c_wobj = cls.sy_c_wobj / float(cls.wesum_obj)

        # weighted symmetric moments, object case:
        cls.s_c_sym_wobj = cls.sx_c_wobj + cls.sy_c_wobj
        cls.m_c_sym_wobj = cls.s_c_sym_wobj / float(cls.wesum_obj_sym)
        cls.Mxx_c_sym_wobj = (1.0 / cls.wesum_obj_sym) * (np.dot((cls.X_weights[:, None] * cls.Xc).T, cls.Xc)
                                                          + np.dot((cls.X_weights[:, None] * cls.Yc).T, cls.Yc))
        cls.Mxy_c_sym_wobj = (1.0 / cls.wesum_obj_sym) * (np.dot((cls.X_weights[:, None] * cls.Xc).T, cls.Yc)
                                                          + np.dot((cls.X_weights[:, None] * cls.Yc).T, cls.Xc))

        return cls

    def test_XX_with_mean(self):
        # many passes
        est = OnlineCovariance(compute_c0t=False, remove_data_mean=False, bessel=False)
        cc = est.fit(self.data).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_lag0)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_lag0)
        cc = est.fit(self.data, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_lag0[:, self.cols_2])

    def test_XX_meanfree(self):
        # many passes
        est = OnlineCovariance(compute_c0t=False, remove_data_mean=True, bessel=False)
        cc = est.fit(self.data).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_lag0)
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_lag0)
        cc = est.fit(self.data, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_lag0[:, self.cols_2])

    def test_XX_weightobj_withmean(self):
        # many passes
        est = OnlineCovariance(compute_c0t=False, remove_data_mean=False, bessel=False)
        cc = est.fit(self.data, n_splits=10, weights=self.data_weights).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_wobj_lag0)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_wobj_lag0)
        cc = est.fit(self.data, column_selection=self.cols_2, weights=self.data_weights).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_wobj_lag0[:, self.cols_2])

    def test_XX_weightobj_meanfree(self):
        # many passes
        est = OnlineCovariance(compute_c0t=False, remove_data_mean=True, bessel=False)
        cc = est.fit(self.data, weights=self.data_weights, n_splits=10).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_wobj_lag0)
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_wobj_lag0)
        cc = est.fit(self.data, column_selection=self.cols_2, weights=self.data_weights).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_wobj_lag0[:, self.cols_2])

    def test_XXXY_withmean(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=False, compute_c0t=True, bessel=False)
        cc = est.fit((self.X, self.Y), n_splits=10).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx)
        np.testing.assert_allclose(cc.mean_t, self.my)
        np.testing.assert_allclose(cc.cov_00, self.Mxx)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy)
        cc = est.fit((self.X, self.Y), n_splits=10, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy[:, self.cols_2])

    def test_XXXY_meanfree(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=True, compute_c0t=True, bessel=False)
        cc = est.fit((self.X, self.Y)).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx)
        np.testing.assert_allclose(cc.mean_t, self.my)
        np.testing.assert_allclose(cc.cov_00, self.Mxx0)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0)
        cc = est.fit((self.X, self.Y), column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx0[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0[:, self.cols_2])

    def test_XXXY_weightobj_withmean(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=False, compute_c0t=True, bessel=False)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_wobj)
        np.testing.assert_allclose(cc.mean_t, self.my_wobj)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_wobj)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_wobj)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_wobj[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_wobj[:, self.cols_2])

    def test_XXXY_weightobj_meanfree(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=True, compute_c0t=True, bessel=False)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_wobj)
        np.testing.assert_allclose(cc.mean_t, self.my_wobj)
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_wobj)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0_wobj)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_wobj[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0_wobj[:, self.cols_2])

    def test_XXXY_sym_withmean(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=False, compute_c0t=True, reversible=True, bessel=False)
        cc = est.fit((self.X, self.Y)).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.m_sym)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_sym)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_sym)
        cc = est.fit((self.X, self.Y), column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_sym[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_sym[:, self.cols_2])

    def test_XXXY_sym_meanfree(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=True, compute_c0t=True, reversible=True, bessel=False)
        cc = est.fit((self.X, self.Y)).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.m_sym)
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_sym)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0_sym)
        cc = est.fit((self.X, self.Y), column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_sym[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0_sym[:, self.cols_2])

    def test_XXXY_weightobj_sym_withmean(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=False, compute_c0t=True, reversible=True, bessel=False)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.m_sym_wobj)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_sym_wobj)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_sym_wobj)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_sym_wobj[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_sym_wobj[:, self.cols_2])

    def test_XXXY_weightobj_sym_meanfree(self):
        # many passes
        est = OnlineCovariance(remove_data_mean=True, compute_c0t=True, reversible=True, bessel=False)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.m_sym_wobj)
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_sym_wobj)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0_sym_wobj)
        cc = est.fit((self.X, self.Y), weights=self.data_weights_lagged, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx0_sym_wobj[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy0_sym_wobj[:, self.cols_2])

    def test_XX_meanconst(self):
        est = OnlineCovariance(compute_c0t=False, bessel=False)
        cc = est.fit(self.data - self.mean_const).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_c_lag0)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_lag0)
        cc = est.fit(self.data - self.mean_const, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_lag0[:, self.cols_2])

    def test_XX_weighted_meanconst(self):
        est = OnlineCovariance(compute_c0t=False, bessel=False)
        cc = est.fit(self.data - self.mean_const, weights=self.data_weights).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_c_wobj_lag0)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_wobj_lag0)
        cc = est.fit(self.data - self.mean_const, weights=self.data_weights, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_wobj_lag0[:, self.cols_2])

    def test_XY_meanconst(self):
        est = OnlineCovariance(compute_c0t=True, bessel=False)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const)).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_c)
        np.testing.assert_allclose(cc.mean_t, self.my_c)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const), column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c[:, self.cols_2])

    def test_XY_weighted_meanconst(self):
        est = OnlineCovariance(compute_c0t=True, bessel=False)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const),
                     weights=self.data_weights_lagged).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.mx_c_wobj)
        np.testing.assert_allclose(cc.mean_t, self.my_c_wobj)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_wobj)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c_wobj)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const),
                     weights=self.data_weights_lagged, column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_wobj[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c_wobj[:, self.cols_2])

    def test_XY_sym_meanconst(self):
        est = OnlineCovariance(compute_c0t=True, reversible=True, bessel=False)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const)).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.m_c_sym)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_sym)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c_sym)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const), column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_sym[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c_sym[:, self.cols_2])

    def test_XY_sym_weighted_meanconst(self):
        est = OnlineCovariance(compute_c0t=True, reversible=True, bessel=False)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const),
                     weights=self.data_weights_lagged).fetch_model()
        np.testing.assert_allclose(cc.mean_0, self.m_c_sym_wobj)
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_sym_wobj)
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c_sym_wobj)
        cc = est.fit((self.X - self.mean_const, self.Y - self.mean_const), weights=self.data_weights_lagged,
                     column_selection=self.cols_2).fetch_model()
        np.testing.assert_allclose(cc.cov_00, self.Mxx_c_sym_wobj[:, self.cols_2])
        np.testing.assert_allclose(cc.cov_0t, self.Mxy_c_sym_wobj[:, self.cols_2])


class TestCovarEstimatorWeightsList(unittest.TestCase):

    def test_weights_close_to_zero(self):
        n = 1000
        data = [np.random.random(size=(n, 2)) for _ in range(5)]

        # create some artificial correlations
        data[0][:, 0] *= np.random.randint(n)
        data = np.asarray(data)

        weights = [np.ones(n, dtype=np.float32) for _ in range(5)]
        # omit the first trajectory by setting a weight close to zero.
        weights[0][:] = 1E-44
        weights = np.asarray(weights)

        est = OnlineCovariance(compute_c0t=True)
        for data_traj, weights_traj in zip(data, weights):
           est.partial_fit((data_traj[:-3], data_traj[3:]), weights=weights_traj[:-3])
        cov = est.fetch_model()
        # cov = covariance_lagged(data, lag=3, weights=weights, chunksize=10)
        assert np.all(cov.cov_00 < 1)

    @unittest.skip("zero weights known to be broken #1117")
    def test_weights_equal_to_zero(self):
        n = 1000
        data = [np.random.random(size=(n, 2)) for _ in range(5)]

        # create some artificial correlations
        data[0][:, 0] *= np.random.randint(n)

        weights = [np.ones(n, dtype=np.float32) for _ in range(5)]
        # omit the first trajectory by setting a weight close to zero.
        weights[0][:] = 0
        weights[0][800:850] = 1

        est = OnlineCovariance(compute_c0t=True)
        for x, w in zip(data, weights):
            est.partial_fit((x[:-3], x[3:]), w[:-3])
        cov = est.fetch_model()
        zeros = sum((sum(w == 0) for w in weights))
        assert np.all(cov.cov_00 < 1), cov.cov_00
        assert np.all(cov.cov_00 > 0), cov.cov_00

        # from statsmodels.stats.weightstats import DescrStatsW
        # ds = DescrStatsW(data, weights=weights)
        # np.testing.assert_allclose(cov.C00_, ds.cov)

    def test_non_matching_length(self):
        n = 100
        data = [np.random.random(size=(n, 2)) for n in range(3)]
        data = (data[:-1], data[1:])
        weights = [np.random.random(n) for _ in range(3)]
        weights[0] = weights[0][:-3]
        with self.assertRaises(ValueError):
            OnlineCovariance(compute_c0t=True).fit(data, weights=weights)

        with self.assertRaises(ValueError):
            OnlineCovariance(compute_c0t=True).fit(data, weights=weights[:10])

    def test_re_estimate_weight_types(self):
        # check different types are allowed and re-estimation works
        x = np.random.random((100, 2))
        x = (x[:-1], x[1:])
        c = OnlineCovariance(compute_c0t=True)
        c.fit(x, weights=np.ones((len(x[0]),))).fetch_model()
        c.fit(x, weights=np.ones((len(x[0]),))).fetch_model()
        c.fit(x, weights=None).fetch_model()
        c.fit(x, weights=x[0][:, 0]).fetch_model()


if __name__ == "__main__":
    unittest.main()
