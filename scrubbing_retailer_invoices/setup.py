try:
    from setuptools import setup
except:
    from distutils.core import setup

config={
    'description':'My Project.',
    'author':'Oliver Oakes',
    'url':'where to get it?'
    'download_url':'where to download it'
    'author_email':'oliver.oakes@salitix.com',
    'version':'0.1',
    'install_requires':['nose'],
    'packages':['pandas'],
    'scripts':[],
    'name':'NAME'
}

setup(**config)
