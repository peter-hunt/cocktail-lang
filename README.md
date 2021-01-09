# The Cocktail Lang
<p align="center">
  <img src="https://img.shields.io/github/stars/peter-hunt/cocktail-lang">
  <img src="https://img.shields.io/static/v1?label=Contributions&message=Welcome&color=0059b3">
  <img src="https://img.shields.io/github/repo-size/peter-hunt/cocktail-lang">
  <img src="https://img.shields.io/github/languages/top/peter-hunt/cocktail-lang">
  <img src="https://img.shields.io/github/license/peter-hunt/cocktail-lang">
</p>

The Cocktail Lang helps you to create speedy and beautiful code easily.


## Installation
Use git to install Cocktail Lang as a folder.
Go to the directory you want to download Regex in, and enter the following command:

```bash
git clone https://github.com/peter-hunt/cocktail-lang.git
```

Or use pip to install it as a package. (recommended)

```bash
pip install git+https://github.com/peter-hunt/cocktail-lang.git
```

This project is using libraries organized for Python 3.8+ built into the directory
Docopt 0.6.2 and Rply 0.7.7 are used.
To install original Dependencies, go to the project's directory and enter these commands
```bash
rm -rf cocktail/rply cocktail/docopt.py
pip install -r requirements.txt
```

This project requires Python 3.8+


## Current State
The features that are currently implemented are as follows:
* Data types: `Boolean`, `Number`, `String`, `Tuple` and `List`
* Data operations (not well-implemented yet)
* Most operators from Python: `+`, `-`, `*`, `/`, etc.
* Comments
* Flow control: if, if/else, for-loop, for-of-loop, while-loop
* Constants
* Functions (Beta, currently not callable)
* User input and system output


## Extension
[Cocktail Lang Support](https://github.com/peter-hunt/peter-hunt.cocktail-lang-support)

WARNING: This extension is unstable, read the instructions carefully before installing.

## Donation
This project is open-source and free-to-use, it would be really helpful to support me!
For more information, please see my [Patreon](https://patreon.com/that_peterhunt).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Example and Testing
To see examples of the Cocktail programs, go to the tests directory.

## License
[MIT](LICENSE.txt)
