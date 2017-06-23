from setuptools import setup

setup(
    name='js9_builder_bootstrap',
    version='9.0.0',
    description='boostrap a zero-os with js9 build env.',
    url='https://github.com/Jumpscale/builder_bootstrap',
    author='GreenItGlobe',
    author_email='info@gig.tech',
    license='Apache',
    packages=['JumpScale9Builder'],
    install_requires=[
        'JumpScale9>=9.0.0',
        'g8core>=1.0.0',
        'pytoml>=0.1.12',
        'redis>=2.10.5',
        'requests>=2.13.0',
        'ovh',
        '0-orchestrator>= 1.1.0a4'
    ],
)
