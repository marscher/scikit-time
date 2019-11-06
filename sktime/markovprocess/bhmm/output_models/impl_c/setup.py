def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration

    config = Configuration('impl_c', parent_package=parent_package, top_path=top_path)
    config.add_extension('discrete', sources=['discrete.pyx', 'src/_discrete.c'],
                         include_dirs=['src'])
    config.add_extension('gaussian', sources=['gaussian.pyx', 'src/_gaussian.c'],
                         include_dirs=['src'])
    return config