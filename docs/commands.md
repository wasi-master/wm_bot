<!-- markdownlint-disable MD033-->
# Commands

First lets know some information about the commands.

- \<argument\>
  - This means the argument is ***required***.<br>
- [argument]
  - This means the argument is ***optional***.<br>
- [argument=x]
  - This means the argument is ***optional*** and if not provided, x is the default value.<br>
- [argument...]
  - This means you can have multiple arguments.<br>

***You do not type in the brackets!***<br>

## Akinator

----------------------------------

### akinator

A command to play a game of akinator

***Aliases:*** `aki`

***Required Bot Permissions:*** This command requires the bot to have following permission(s): `Use External Emojis`

![Command Example](https://i.imgur.com/r6086QT.gif)


## Animals

----------------------------------

### cat

Sends a random random cute cat picture

***Aliases:*** `kitty`

![Command Example](https://i.imgur.com/J8vTsyK.gif)


### dog

Sends a random random cute dog picture

***Aliases:*** `doggo`, `puppy`

![Command Example](https://i.imgur.com/nJIyoLq.gif)


### panda

Sends a random random cute panda picture

***Aliases:*** `pnd`

![Command Example](https://i.imgur.com/GjsQ5AB.gif)


### redpanda

Sends a random random cute red panda picture

***Aliases:*** `rdpnd`

![Command Example](https://i.imgur.com/jgjohiu.gif)


### koala

Sends a random cute koala picture

***Aliases:*** `kl`

![Command Example](https://i.imgur.com/y8VhA8d.gif)


### bird

Sends a random cute bird picture

***Aliases:*** `birb`

![Command Example](https://i.imgur.com/wittKiF.gif)


### racoon

Sends a random racoon picture

***Aliases:*** `rcn`

![Command Example](https://i.imgur.com/u7xuVvG.gif)


### kangaroo

Sends a random kangaroo picture

***Aliases:*** `kng`

![Command Example](https://i.imgur.com/rPvwWVW.gif)


### fox

Sends a random high quality fox picture

***Aliases:*** `fx`

![Command Example](https://i.imgur.com/eHN5GZT.gif)


## Anime

----------------------------------

### waifu

Sends a waifu

Sends [Waifu](https://www.dictionary.com/e/fictional-characters/waifu) pictures<br>Note: This command is nsfw only
## Calculator

----------------------------------

### calc \<formula\>

Evaluate math expressions.

***Aliases:*** `math`, `calculator`, `calculate`

![Command Example](https://i.imgur.com/P6PbUDi.png)


## Claptrap

----------------------------------

### claptrap

Can I shoot something now? Or climb some stairs? SOMETHING exciting? (has 500+ texts. can you get them all?)

***Aliases:*** `ct`

![Command Example](https://i.imgur.com/igq43W3.png)


## Coding

----------------------------------

### regex \<regex\> \<text\>

Matches text to the regex provided

![Command Example](https://i.imgur.com/Tab4FUF.gif)


### json \<json_string\>

Formats the given json string

![Command Example](https://i.imgur.com/vsABmqr.gif)


### diff \<first\> \<second\>

Sends the unified todifference between first and second<br>Note: if the text is small or the difference is not very large you should use the `ndiff` command

***Aliases:*** `difference`, `dif`
### ndiff \<first\> \<second\>

Sends the only difference between first and second<br>Note: there is another diff command that can be used instead for<br>large texts and difference between multiple lines

***Aliases:*** `ndifference`, `ndif`
### stackoverflow

***Aliases:*** `so`
### pypi \<package_name\>

Gets information about the specified pypi package

***Aliases:*** `pypl`, `pip`

![Command Example](https://i.imgur.com/5MdrujN.gif)


### pypi_search \<package_search\>

Searches pypi andreturns top 100 results

***Aliases:*** `pypi-search`, `pipsearch`, `pypis`, `pips`

***Required Bot Permissions:*** This command requires the bot to have following permission(s): `Use External Emojis`

![Command Example](https://i.imgur.com/xQK85rO.gif)


### crates \<package_name\>

Searches crates for rust packages

***Aliases:*** `crt`, `cargo`
### rubygem \<package_name\>

Searches rubygems for ruby packages

***Aliases:*** `gem`, `rg`
### github \<repo\>

Shows information about a GitHub repository

***Aliases:*** `gh`
### npm \<package_name\>

Searches npm for node packages
### rtfs \<search\>

Gets the source for an object from the discord.py library
## Colors

----------------------------------

### color \<color\>

Sends information about a color<br>The following formats are accepted:<br><br>- `0x<hex>`<br>- `#<hex>`<br>- `0x#<hex>`<br>- `rgb(<number>, <number>, <number>)`<br>- All the colors mentioned in https://gist.github.com/Soheab/d9cf3f40e34037cfa544f464fc7d919e#colours

***Aliases:*** `col`, `colour`

![Command Example](https://i.imgur.com/zMQ7mz3.png)


### randomcolour

Generates a random color.<br>Note: This is not fully random, but it is random enough for most purposes.

***Aliases:*** `randcolor`, `randomcol`, `randcol`, `randomcolor`, `rc`

![Command Example](https://i.imgur.com/m6GQHPg.png)


## Cryptography

----------------------------------

### base64

Command for encoding and decoding text from and to [base64](https://en.wikipedia.org/wiki/Base64)

***Aliases:*** `b64`
### binary \<text\>

Converts text to binary, can take both a number or a string

***Aliases:*** `bin`
### unbinary \<binary_number\>

Converts binary to text, the input needs to be encoded in binary format

***Aliases:*** `unbin`
## Data

----------------------------------

### lyrics \<song_name\>

Sends the lyrics of a song

***Aliases:*** `lrc`

***Required Bot Permissions:*** This command requires the bot to have following permission(s): `Use External Emojis`
### pokedex \<pokemon\>

Sends the details about a [pokemon](https://en.wikipedia.org/wiki/Pok%C3%A9mon)

***Aliases:*** `pd`

***Required Bot Permissions:*** This command requires the bot to have following permission(s): `Use External Emojis`
### covid [area]

Coronavirus Stats

Sends statistics about the corona virus situation of a country<br>The area defaults to `global` if not specified
### fact

Sends a random fact

***Aliases:*** `randomfact`, `rf`, ` f`
### movie \<query\>

See details about a movie

Sends information about a movie
### screenshot \<website\>

Sends the screenshot of a website

***Aliases:*** `ss`
### gender \<name\>

Get the gender of the person with the name specified
### weather \<location\>

Sends the weather information of a specific location
## English

----------------------------------

### define \<word\>

Sends the definition of a word

***Aliases:*** `def`, `df`

***Required Bot Permissions:*** This command requires the bot to have following permission(s): `Use External Emojis`
### translate [lang] \<text\>

Translates a text to another language if specified, defaults to English

***Aliases:*** `tr`
## Fun

----------------------------------

### random_identity [results=1]

Sends all details about a randomly generated person that does not exist.

***Aliases:*** `randomuser`, `randomdude`, `randomperson`, `ruser`, `rdude`, `rperson`, `randomidentity`
### cookie

Who can catch the cookie first?

***Aliases:*** `co`
### nevergonnagiveyouup \<whotogiveup\>

Textual rickroll, sends the rickroll lyrics with the name being the person specified

***Aliases:*** `giveyouup`, `gyu`, `nggyu`, `never_gonna_give_you_up`, `rickroll`
### snipe [channel]

Sends the last deleted message in the channel, can be unavailable

***Server Only:*** This command can only be used in a server
### imagine \<thing\>

Tells you if the bot can imagine the thing
### cakeday

Shows the people who has their discord birthday today, inspired by reddit

***Server Only:*** This command can only be used in a server
### advice

Gives a random advice
### topic

Gives a random topic to discuss
### brawlstarsmap \<provided_map\>

***Aliases:*** `bsm`, `bsmap`, `map`
### groot

Who... who are you?
### howgay [member]

Shows how gay a person is (random)

***Aliases:*** `hg`, `howlesbian`, `hl`

***Server Only:*** This command can only be used in a server
### meme

Sends a random meme

***Aliases:*** `mem`
### rockpaperscissors

Play the classic rock paper scissors game

***Aliases:*** `rps`

***Server Only:*** This command can only be used in a server
### chatbot

Talk to AI Chatbot

***Aliases:*** `cb`
### penis [member]

See someone's penis size (random)

***Aliases:*** `pp`, `ppsize`

***Server Only:*** This command can only be used in a server
### emojiparty

The bot will send the name of every emoji reacted to the bot's message
## Image

----------------------------------

### qrcode \<text\>

Converts the given text to a [qr code](https://en.wikipedia.org/wiki/QR_code)

***Aliases:*** `qr`

![Command Example]()


### rounden [member]

***Aliases:*** `circle`, `round`, `circular`
### pixel [member]
### allmyhomiesuse \<bad\> \<good\>

***Aliases:*** `amhu`
### retromeme \<top\> \<bottom\> [url]
### modernmeme \<top\> \<bottom\> [url]
### america [member]
### triggered [member]
### colors [member]
### communism [member]
### wasted [member]
### fiveguys [member] [member2]
### whygay [member] [member2]
### invert [member]
### bomb [member]
### sobel [member]
### triangle [member]
### angel [member]
### satan [member]

***Aliases:*** `s8n`
### delete [member]
### fedora [member]
### worsethanhitler [member]

***Aliases:*** `hitler`, `wth`
### wanted [member]
### youtubecomment \<member\> \<text\>

***Aliases:*** `ytcomment`
### discord \<member\> \<text\>
### jail [member]
### pride [flag=gay] [member]
### trash [member]
### magik [member]
### paint [member]
### captcha \<text\> [member]
### clyde \<message\>
### stickbug [member]
### changemymind \<message\>

***Aliases:*** `cmm`
### phcomment \<member\> \<message\>

***Aliases:*** `phc`, `pornhubcomment`
### iphone [member]

***Aliases:*** `iphonex`
### jpeg [member]
## Information

----------------------------------

### inviteinfo \<invite\>

Get information about an invite

***Aliases:*** `ii`
### channelinfo [channel]

See information about a specific channel.

***Aliases:*** `ci`, `chi`
### roleinfo \<role\>

See information about a role

***Aliases:*** `ri`, `rlinf`
### emojiinfo \<emoji\>

Shows info about a emoji

***Aliases:*** `ei`, `emoteinfo`
## MadLibs

----------------------------------

### madlibs

Let's play MadLibs!
## Messages

----------------------------------

### firstmessage [channel]

Sends the first message in a specified channel, defaults to the current channel

***Aliases:*** `fm`
### rawembed \<message\>

Shows raw embed json of a message gotten from the discord API

***Aliases:*** `re`
### rawjson \<message\>

Shows raw json of a message gotten from the discord API

***Aliases:*** `rj`
### rawchannel \<channel\>

Shows raw json of a channel gotten from the discord API

***Aliases:*** `rch`
### getemojis \<msg\>

Gets all the emojis from a specified message and returns them in a zip file

***Aliases:*** `gm`
### rawprofile \<user\>

Shows raw json of a user's profile gotten from the discord API

***Aliases:*** `rawuser`, `rs`
### rawmessage \<message\>

See a raw version of a message<br><br>For example if someone sends a cool text formatted with bold/italics and stuff and you wanna copy it but keep the formatting

***Aliases:*** `raw`
### messages [user] [channel]

See someone's messages in a channel, defaults to the command invoker
### top [limit=500] [channel]

See a list of top active users in a channel
## Meta

----------------------------------

### commandsearch \<cmd\>

Search for a command in the bot

***Aliases:*** `cs`
### hello

Use this to know if the bot is online or not
### lines

Shows the amount of lines and some other information about the bot's code

***Aliases:*** `linecount`, `lc`
### ping

Shows the bot's speed

***Aliases:*** `p`
### support

Get a invite link to the bot's support server
### botinfo

Lists some general stats about the bot.

***Aliases:*** `info`
### suggest \<suggestion\>

***Aliases:*** `sug`, `suggestion`, `rep`, `report`
### source [command]

Displays the bot's full source code or source code for a specific command.<br><br>To display the source code of a subcommand you can separate it by<br>periods, e.g. `tag.create` for the create subcommand of the tag command<br>or by spaces e.g. `tag create`.
### users

Shows the top 10 bot users

***Aliases:*** `usr`, `user`
### usage

Shows usage statistics about commands

***Aliases:*** `usg`, `usages`
### uptime

Shows how long the bot is online for

***Aliases:*** `upt`
### cleanup [search=100]

Cleans up the bot's messages from the channel.<br><br>If a search number is specified, it searches that many messages to delete.<br>If the bot has Manage Messages permissions then it will try to delete<br>messages that look like they invoked the bot as well.<br>After the cleanup is completed, the bot will send you a message with<br>which people got their messages deleted and their count. This is useful<br>to see which users are spammers.<br>You must have Manage Messages permission to use this.

***Aliases:*** `clnup`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Messages`
### invite [bot]

Send a invite link for the bot. if another bot is specified, sends the invite link for that bot instead

***Aliases:*** `botinvite`, `inv`
### stats

Sends some statistics about the bot

***Aliases:*** `statistics`
### help [command]

Shows this message
## Miscellaneous

----------------------------------

### say [channel] \<text\>

Says what you want the bot to say.<br><br>If channel is specified then says the thing in that channel, if it is not specified then uses the current channel<br>you can't mention people in the message

***Aliases:*** `speak`, `echo`, `s`
### websiteping \<url\>

***Aliases:*** `webping`, `pingweb`, `wp`, `pw`
### timing [time=10]

Test your timing!<br><br>As soon as the message shows, click on the reaction after some amount of seconds, by default 10<br>Maximum time is 60 seconds and minimum time is 1 second

***Aliases:*** `t`
## Moderation

----------------------------------

### kick \<member\> [reason]

Kicks a member from the server.

***Required Permissions:*** This command requires the following permission(s) to use: `Kick Members`
### nick \<member\> \<nick\>

Changes the nickname of a person

***Aliases:*** `setnick`, `setnickname`, `nickname`, `changenickname`, `chnick`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Nicknames`
### ban \<member\> [reason]

Bans a member from the server.

***Required Permissions:*** This command requires the following permission(s) to use: `Ban Members`
### recentbans

Shows the recent bans, who banned them and why

***Aliases:*** `rb`

***Required Permissions:*** This command requires the following permission(s) to use: `View Audit Log`
### unban \<user\>

Bans a user by their name#discriminator or their name or their id

***Required Permissions:*** This command requires the following permission(s) to use: `Ban Members`
### prune \<amount\>

Removes messages from the current server.

***Aliases:*** `clear`, `purge`, `c`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Messages`

***Server Only:*** This command can only be used in a server
### mute \<user\> [reason]

Mutes a user with a optional reason<br><br>If the guild has a muted role then it uses that role and if not, creates a muted role
### unmute \<user\>

Unmutes a muted member

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Roles`
### slowmode [channel] [slowmode]

Change the current slowmode of the channel,<br><br>The slowmode and channel are optional, slowmode defaults to 5 and channel defaults to the current channel

***Aliases:*** `sd`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
### role \<member\> \<role\>

Changes roles for a member<br><br>Removes if he has the role, adds the role if not

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Roles`
### perms [member] [channel]

See someone's permissions

***Aliases:*** `permissions`
### nuke [channel]

Nukes a channel<br><br>Creates a new channel with all the same properties (permissions, name, topic etc.)<br>and deletes the original one

***Aliases:*** `nk`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
### clone [channel]

Clones a channel<br><br>Creates a duplicate channel with all the same properties (permissions, name, topic etc.)

***Aliases:*** `cln`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
### lock [role]

Locks a channel,<br><br>it denys permission to send messages in a channel for everyone or the role specified

***Aliases:*** `lck`, `lk`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
### unlock [role]

Unocks a channel,<br><br>it allows permission to send messages in a channel for everyone or the role specified

***Aliases:*** `unlck`, `ulk`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
### block \<user\>

Blocks a user from chatting in current channel.

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
### unblock \<user\>

Unblocks a previously blocked user from the channel

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Channels`
## Owner

----------------------------------

### bot_message

To do stuff with the bot's messages

***Aliases:*** `msg`
### leaveserver

This makes the bot leave the server
### shutdown

Shuts the bot down

***Aliases:*** `shutup`
### blockfromusingthebot \<task\>

Blocks the specified user from using the bot.

***Aliases:*** `bfutb`, `bfb`, `blockfrombot`
### reinvoke [message]

Re-invokes the command gotten from the message<br><br>You can also reply to the message to get the command from it

***Aliases:*** `rein`
### get \<url\>

Returns the response from the specified website url

***Aliases:*** `curl`
### eval \<cmd\>

Evaluates input.<br>Input is interpreted as newline seperated statements.<br>If the last statement is an expression, that is the return value.<br>Usable globals:<br>- `bot`: the bot instance<br>- `discord`: the discord module<br>- `commands`: the discord.ext.commands module<br>- `ctx`: the invokation context<br>- `__import__`: the builtin `__import__` function<br>Such that `>eval 1 + 1` gives `2` as the result.<br>The following invokation will cause the bot to send the text '9'<br>to the channel of invokation and return '3' as the result of evaluating<br>>eval ```<br>a = 1 + 2<br>b = a * 2<br>await ctx.send(a + b)<br>a<br>```

***Aliases:*** `e`
## Random

----------------------------------

### choosebestof [times] [choices...]

Chooses between multiple choices N times.
### 8ball \<question\>

The user asks a yes-no question to the ball, then the bot reveals an answer.

***Aliases:*** `eightball`, `eight ball`, `question`, `answer`, `8b`
### choose \<choices\>

Chooses a random item from a list of items.

***Aliases:*** `pick`, `choice`, `ch`
### randomcommand

Sends a random command for you to try

***Aliases:*** `rcmd`
## Reddit

----------------------------------

### subreddit \<subreddit\> [post_filter]

Gets a random post from a subreddit<br><br>you can pass a optional post_filter that is either hot or top.<br>so a command with hot as the post_filter would look like<br>`subreddit r/memes hot`

***Aliases:*** `sr`
## Search

----------------------------------

### wikipedia \<search_term\>

Searches wikipedia for specific search term

***Aliases:*** `wiki`, `searchwiki`
### google \<search_term\>

Searches google for specific search term

***Aliases:*** `search`, `g`
### fake_person

Sends the image of a fake person generated by AI

***Aliases:*** `fakeperson`, `fp`, `thispersondoesnotexist`, `tpdne`
### random_image [vertical=False]

Sends a random image, if vertical is True, sends a vertical image

***Aliases:*** `randomimage`, `rndi`, `randompicture`, `randompic`, `rp`
### image \<search_term\>

Searched google for the image, uses [google image search](https://images.google.com)

***Aliases:*** `imagesearch`, `is`, `i`
### youtube \<text\>

Searches youtube for specific title

***Aliases:*** `yt`
### gif \<query\>

Sends a gif from tenor

***Aliases:*** `tenor`
### youtubeinfo \<video_url\>

***Aliases:*** `yti`, `ytinfo`, `youtubei`, `videoinfo`, `youtubevideoinfo`, `ytvi`, `vi`
## Server

----------------------------------

### prefix \<prefix\>

Changes the prefix for a server

***Aliases:*** `setprefix`, `setwmbotprefix`

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Guild`
### serverinfo

See the information of the current server

***Aliases:*** `guildinfo`, `si`, `gi`
### boosters

Sends all the boosters of this server
### memberlist

See all the members of this server sorted by their top role

***Aliases:*** `memlist`, `allmembers`, `am`, `servermembers`, `sm`, `memberslist`
### firstjoins

See all the members of this server sorted by their join time

***Aliases:*** `fj`, `whojoinedfirst`, `wjf`, `firstmembers`, `fmem`, `oldmembers`
### newjoins

See the newest members of this server

***Aliases:*** `nj`, `whojoinedlast`, `wjl`, `lastmembers`, `lm`, `newmembers`
### bots

See all the bots in this server sorted by their join date
### humans

Sends all the humans of this server sorted by their join date
### emoji \<task\> \<emoji_name\>

Adds a emoji from https://emoji.gg to your server

***Required Permissions:*** This command requires the following permission(s) to use: `Manage Emojis`
### badges [server]

Shows the amount of badges in the server. Kind of a useless command.

***Aliases:*** `flags`
## Tags

----------------------------------

### tag

Shows the content of a tag

***Aliases:*** `tg`
### tags \<member\>

Show all tags of a user

***Aliases:*** `every`
## Text

----------------------------------

### typeracer

See your typing speed

***Aliases:*** `trc`
### randomcase \<inp\>

Converts the given input to a random case<br><br>For example "hello my name is wasi" can become "hELlO mY NamE is WaSI"
### hastebin \<data\>

Pastes the given data to hastebin and returns the link
### spoiler \<text\>

Spoilers a text letter by letter
### reverse \<text\>

Reverses a text
### boxspoilerrepeat \<width\> \<height\> \<text\>

Box shaped spoilers and repeats a text

***Aliases:*** `bsr`
### repeat \<amount\> \<text\>

Repeats a text
### morse \<text\>

Morse code :nerd:
### unmorse \<text\>

English to morse
### abbreviations \<text\>

See the meaning of a texting abbreviation<br><br>Like "idk" means "I don't know"

***Aliases:*** `avs`, `abs`, `whatdoesitmeanwdim`
### texttospeech \<lang\> \<text\>

Converts some text to speech (TTS)

***Aliases:*** `tts`
### charinfo \<characters\>

Sends information about a character 🤓

***Aliases:*** `chrinf`, `unicode`, `characterinfo`
### emojify \<text\>

Emojify a text

***Aliases:*** `fancy`, `emf`, `banner`
### charactercount \<text\>

***Aliases:*** `cc`, `charcount`
### uwuify \<text\>

uwuifies a given text

***Aliases:*** `uwu`
### ascii [text]
### zalgo \<message\>

Ỉ s̰hͨo̹u̳lͪd͆ r͈͍e͓̬a͓͜lͨ̈l̘̇y̡͟ h͚͆a̵͢v͐͑eͦ̓ i͋̍̕n̵̰ͤs͖̟̟t͔ͤ̉ǎ͓͐ḻ̪ͨl̦͒̂ḙ͕͉d͏̖̏ ṡ̢ͬö̹͗m̬͔̌e̵̤͕ a̸̫͓͗n̹ͥ̓͋t̴͍͊̍i̝̿̾̕v̪̈̈͜i̷̞̋̄r̦̅́͡u͓̎̀̿s̖̜̉͌...
## TicTacToe

----------------------------------

### tictactoe [player1] [player2]

***Aliases:*** `ttt`
## Time

----------------------------------

### remind \<time\> \<text\>

Remind you to do something after the specified time.
### timeset \<timezone\>

Set your time zone to be used in the time command

***Aliases:*** `tzs`, `timezoneset`, `settimezone`, `stz`, `ts`
### time [location]

See time

See someones time or your time<br><br>The person needs to have their time zone saved

***Aliases:*** `tm`
## Users

----------------------------------

### notawayfromkeyboard

Removes your afk status

***Aliases:*** `nafk`, `unafk`, `rafk`, `removeafk`, `dafk`, `disableafk`
### awayfromkeyboard [reason]

Sets your afk status

***Aliases:*** `afk`
### avatar [user]

See someone's avatar, if user is not provided then it shows your avatar

***Aliases:*** `pfp`, `av`, `profilepicture`, `profile`
### userinfo [member]

Shows info about a user

***Aliases:*** `ui`, `whois`, `wi`, `whoami`, `me`
### spotify [member]

See your or another users spotify info

***Aliases:*** `spt`
## Utility

----------------------------------

### unshorten \<url\>

Got a shortened link? bit.ly? use this command to un shorten the link!<br><br>Does not work for website that do not redirect you to the long url directly.

***Aliases:*** `redirect`, `unshort`, `us`
### id \<snowflake_id\>

Show the date a snowflake ID was created

***Aliases:*** `snowflake`, `snf`
### idinfo \<snowflake_id\>

Show all available data about a snowflake ID

***Aliases:*** `snowflakeinfo`, `snfi`, `idi`
### parsetoken [token]

Parses a token and sends who the token is for<br><br>The token can be provided in the message or the message can be a reply to another message containing the token

***Aliases:*** `pt`
### redirects \<url\>

Sends all the websites a certain websites redirects to

***Aliases:*** `rd`
### embed \<embed_json\>
### dm [message]

Sends you a direct message containing the message specified
### getusers \<role\>

Sends the names of all the people in the role specified

***Aliases:*** `members`
### tos \<term\>

Searches discord terms of service
### dice

Rolls a dice and gives you a number ranging from 1 to 6
### pokemonhack [channel]

Tells you which pokemon it is that has been last spawned by a bot

***Aliases:*** `ph`, `catch`
### saveallemojis

Saves all the emojis in the current server to a zip file and sends the zip file

***Aliases:*** `sae`, `getallemojis`, `gae`