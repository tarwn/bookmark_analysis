from setuptools import setup

setup(name='bookmark_analysis_exploration',
      version='2.0',
      description='Exploratory code for bookmark analysis',
      url='https://github.com/tarwn/bookmark_analysis',
      author='Eli Weinstock-Herman (@tarwn)',
      author_email='tarwn@tiernok.com',
      license='MIT',
      packages=[],
      install_requires=[
          'requests',
          'beautifulsoup4',
          'click',
          'nltk',
          'networkx',
          'numpy'
      ],
      zip_safe=False)
