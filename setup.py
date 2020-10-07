import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='Aesthetician',
     version='0.0.1',
     author="ForOhForError",
     description="CLI FFXIV Character Appearance Manager",
     long_description=long_description,
     long_description_content_type="text/markdown",
     packages=setuptools.find_packages(),
     install_requires=[],
     classifiers=[
         "Programming Language :: Python :: 3",
         "Operating System :: OS Independent",
     ],
     py_modules=['aesthetician', 'data_coding'],
     entry_points={'console_scripts': ['aesthetician = aesthetician:main']},
 )
