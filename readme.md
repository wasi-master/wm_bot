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
  <a href="https://github.com/wasi_master/wm_bot">
    <!-- <img src="images/logo.png" alt="Logo" width="80" height="80"> -->
  </a>

  <h1 align="center">WM Bot</h1>

  <p align="center">
    A advanced bot with more than 220 commands to fit your needs
    <br />
    <a href="docs/commands.md"><strong>Explore the commands »</strong></a>
    <br />
    <br />
    <a href="https://github.com/wasi_master/wm_bot">View Demo</a>
    ·
    <a href="https://github.com/wasi_master/wm_bot/issues">Report Bug</a>
    ·
    <a href="https://github.com/wasi_master/wm_bot/issues">Request Feature</a>
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

I started learning python around March 2020. This project was started as a way to become better at python in July 7th 2020. And the code you'll see in this repository was written between then and now. some code may have really bad practices because of it. if you find any issues with the code, please report them to me in my discord: `Wasi Master#6969` or open a pull request. if you find any bugs or have any ideas then open a issue in the repository

### Built With

* [python](https://python.org)
* [discord.py](https://github.com/Rapptz/discord.py/)
* [dpylint](https://pypi.org/project/dpylint/)
* [vscode discord.py snippets](https://marketplace.visualstudio.com/items?itemName=WasiMaster.discord-py-snippets)

<!-- GETTING STARTED -->
## Getting Started

Almost every folder on this repository has a readme file that you can check for more information on what that specific folder is for
<details>
<summary>To get a local copy up and running follow these simple steps.</summary>

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

* **python**:
  Download and install python 3.8+ from <https://python.org>
* **git**:
  Download and install git from <https://git-scm.com>
* **postgresql**
  Download and install postgresql from <http://www.postgresql.org>

### Instructions

1. Clone the repo

   ```sh
   git clone https://github.com/wasi_master/wm_bot.git
   ```

2. Change directory to the cloned repo

   ```sh
   cd wm_bot
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

4. Edit the config files to add your bot token and the database credentials. (For instructions see the `readme.md` file in each config directory)
5. Run the required commands in your database

    ```bash
    psql username -h hostname -d database_name -f db_setup.sql
    ```

    And replace `username` with your username. `hostname` with your database hostname and `database_name` with your database name.

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

If you want to copy any code from this repo please keep these in mind

* Read the [license](license) and what it allows and disallows
* If you want to copy a whole command
  1. If you are in a cog keep `@commands.command` and if you are not in a command replace `@commands.command` with `@bot.command` or `@client.command` depending on what you named your bot

* If you see any functions/classes that you don't understand/don't know where it is defined, in the desktop version of github you can click the function/class name and see where it is defined

<!-- BAD PRACTICE -->
## Bad Practice, Code, or Code Style

If you find any code that you think is bad practice, code, or code style, please report it to me in my discord: `Wasi Master#6969` or open a pull request or a issue. if you find any bugs or have any ideas then open a issue in the repository

<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](docs/commands.md)_

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

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

* Discord: [Wasi Master#6969](https://discord.com/users/723234115746398219)<br>
* Email: arianmollik323@gmail.com<br>

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Python](https://python.org)
* [discord.py](https://github.com/Rapptz/discord.py/)
* [Postgresql](http://www.postgresql.org)
* My friends at the [discord.py discord server](https://discord.gg/dpy)
