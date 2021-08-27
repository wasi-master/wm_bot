<!-- markdownlint-disable MD033-->
# Welcome

![code size](https://img.shields.io/github/languages/code-size/wasi-master/wm_bot)
![lines of code](https://img.shields.io/tokei/lines/github/wasi-master/wm_bot)
![open issues](https://img.shields.io/github/issues/wasi-master/wm_bot)
![closed issues](https://img.shields.io/github/issues-closed/wasi-master/wm_bot)
![license](https://img.shields.io/github/license/wasi-master/wm_bot)
![forks](https://img.shields.io/github/forks/wasi-master/wm_bot?style=social)
![stars](https://img.shields.io/github/stars/wasi-master/wm_bot?style=social)
![last commit](https://img.shields.io/github/last-commit/wasi-master/wm_bot)
![contributors](https://img.shields.io/github/contributors/wasi-master/wm_bot)

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/wasi-master/wm_bot">
    <!-- <img src="images/logo.png" alt="Logo" width="80" height="80"> -->
  </a>

  <h1 align="center">WM Bot</h1>

  <p align="center">
    With over 220 commands, this powerful bot can be tailored to meet your needs
    <br />
    <a href="docs/commands.md"><strong>Explore the commands »</strong></a>
    <br />
    <br />
    <a href="https://github.com/wasi-master/wm_bot">View Demo</a>
    ·
    <a href="https://github.com/wasi-master/wm_bot/issues">Report Bug</a>
    ·
    <a href="https://github.com/wasi-master/wm_bot/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#copying-code">Copying Code</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

<!-- [![WM Bot Screen Shot][product-screenshot]](https://example.com) -->

Around March 2020, I began learning Python. On July 7th, 2020, I started this project as a way of improving my knowledge of Python. I've written the code in this repository between then and now, so it may contain some bad practices. I would appreciate it if you reported any issues to me in my Discord: `Wasi Master#6969` or opened a pull request. Please open an issue if you see any bugs or have any suggestions

### Built With

* [python](https://python.org)
* [discord.py](https://github.com/Rapptz/discord.py/)
* [dpylint](https://pypi.org/project/dpylint/)
* [vscode discord.py snippets](https://marketplace.visualstudio.com/items?itemName=WasiMaster.discord-py-snippets)

<!-- GETTING STARTED -->
## Getting Started

This repository has a readme file for almost every folder so you can learn more about what is contained in that folder
<details>
<summary>To get a local copy up and running follow these simple steps.</summary>

### Prerequisites

The following are the things you need to install in order to run the bot

* **python**:
  Download and install python 3.8+ from <https://python.org>
* **git**:
  Download and install git from <https://git-scm.com>
* **postgresql**
  Download and install postgresql from <http://www.postgresql.org>

### Instructions

1. Clone the repo

   ```sh
   git clone https://github.com/wasi-master/wm_bot.git
   ```

2. Change directory to the cloned repo

   ```sh
   cd wm_bot/src
   ```

3. Rename the folder config_example to config
   * Linux/MacOS:

   ```bash
   mv config_example config
   ```

   * Windows:

   ```sh
   ren config_example config
   ```

4. Insert the bot token and database credentials into the config files. (Instructions are in each directory's *readme.md* file)

5. Run the required commands in your database (either use this command or do it another way)

    ```bash
    psql <username> -h <hostname> -d <database_name> -f db_setup.sql
    ```

    And don't forget to replace `<username>` with your username. `<hostname>` with your database hostname and `<database_name>` with your database name.

6. Install Required packages

   ```sh
   pip install -r requirements.txt
   ```

7. Run the bot
   * Windows:

   ```sh
   py main.py
   ```

   * Linux:

   ```sh
   python main.py
   ```

   * MacOS:

   ```sh
   python3 main.py
   ```

</details>

<!-- COPYING GUIDE -->
## Copying Code

Keep these things in mind if you want to copy any code from this repo

* Read the [license] (license) and learn what it permits and disallows
* To copy a whole command:
  1. Keep *@commands.command* if you are in a cog; otherwise, replace *@commands.command* with *@bot.command* or *@client.command*, according to what your bot instance is named

* Whenever you see a function/class you are unsure about, you can click the name in the desktop version of github to find out where it is defined

<!-- BAD PRACTICE -->
## Bad Practice, Code, or Code Style

Whenever you find anything that you believe is bad practice, code, or code style, let me know in my discord: *Wasi Master#6969* or open an issue/pull request. Please open an issue if you see any bugs or have any suggestions

<!-- USAGE EXAMPLES -->
## Usage

_For a list of commands this bot has, please refer to the [Documentation](docs/commands.md)_

<!-- CONTRIBUTING -->
## Contributing

Contributions are what makes the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Add or Change some cool code
3. Format the code with ```black``` and ```isort```
   * black: <https://github.com/ambv/black>

     ```sh
     pip install black
     black . # to format all files
     black file.py # to format a single file
     ```

   * isort: <https://github.com/timothycrosley/isort>

     ```sh
     pip install isort
     isort . # to sort all files
     isort file.py # to sort a single file
     ```

4. Commit your Changes
5. Push your code
6. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<!-- CONTACT -->
## Contact

### Wasi Master

* Discord: [Wasi Master#6969](https://discord.com/users/723234115746398219)\
* Email: arianmollik323@gmail.com\

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Python](https://python.org)
* [discord.py](https://github.com/Rapptz/discord.py/)
* [Postgresql](http://www.postgresql.org)
* My friends at the [discord.py discord server](https://discord.gg/dpy)
