import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

install_requires = [
    'tabulate>=0.8.7',
    'fire>=0.3.1'
]

setuptools.setup(
	name = "fr-cli",
	version = "1.0.0",
	description = "Command Line Interface for Freshrelease",
	author = "Bharathi Kannan",
	long_description = long_description,
	url = "https://github.com/bharathikannan-zarget/fr-cli",
	packages = setuptools.find_packages(),
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: Freshworks proprietary license",
		"Operating System:: Os Independent",
	],
	scripts=['bin/fr-cli'],
	python_requires='>=3.6'
)
