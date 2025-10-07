---
description: '[Upsolved] A white box web exploitation CTF challenge from Compfest 17'
---

# \[Web] Basssh

## TL;DR

* A Website made with bash (Crazy ik) that takes a filename as an argument.
* the filename is then urldecoded and filtered with basename. after that the server read the file and return it to the client.&#x20;
* a parameter injection is possible. Using -z -a its possible to craft a ../../ and get the flag at /flag.txt

Flag: Upsolved so no flag :(

## Description

I didn't save it lmao. Next time I'll do better, I swear

## Overview

So we have this website made with bash that gives a CLI like interface where we can pick a python file from the three files that were given. The selected python files can then be executed with our input.&#x20;

<figure><img src="../../.gitbook/assets/image (11) (1).png" alt=""><figcaption></figcaption></figure>

The Interesting part here is when selecting a file it's just adding an argument to the current page&#x20;

```
/?filename=selected_python_file.py
```

Looking at the following source code,

<figure><img src="../../.gitbook/assets/image (13) (1).png" alt=""><figcaption></figcaption></figure>

<figure><img src="../../.gitbook/assets/image (14) (1).png" alt=""><figcaption></figcaption></figure>

We can see that the filename argument is being passed to the _<mark style="color:$success;">urldecode</mark>_ command which is a custom command that just do what the command name suggest.&#x20;

After that, the input is then passed to the _<mark style="color:$success;">basename</mark>_ command and passed again to be read with _<mark style="color:$success;">cat</mark>_ and is then get showed to the client

<figure><img src="../../.gitbook/assets/image (15) (1).png" alt=""><figcaption></figcaption></figure>

From this Dockerfile, we can see that the flag resides in /flag.txt\
so we must find a way to read there or find an RCE.

Other parts of the code is a lot of Red Herring that is just unused by the website or is just a logical functionalities of a web server but made in bash.

## Solution

The most important part of the code is the file reading of any input from the user. Of course, the there is a filter of the input using _<mark style="color:$success;">basename</mark>_ that stops us from just doing a simple ../../../flag.txt

The key is that we can do a <mark style="color:$warning;">parameter injection</mark> in the filename input. We can leverage that to our advantage. See the manual for _<mark style="color:$success;">basename</mark>_,

<figure><img src="../../.gitbook/assets/image (16) (1).png" alt=""><figcaption></figcaption></figure>

From the manual, We can see the parameter <mark style="color:$success;">-z</mark> and <mark style="color:$success;">-a</mark>. Those two parameter are the key to solving this challenge.

With the <mark style="color:$success;">-a</mark> parameter, we can make the command take multiple inputs and output multiple result as well:

```
> basename -a /home/fl /home/ag.txt
fl
ag.txt
```

And with the <mark style="color:$success;">-z</mark> parameter, we can make those multiple output to end not with a newline but with a null:

```
> basename -z -a /home/fl /home/ag.txt
flag.txt
```

With this trick we can craft a payload that will make a ../../../\
payload:

```
> basename -z -a .. / .. / .. / flag.txt
../../../flag.txt
```

With this we gain the ability for path traversal and we obtain the flag

<figure><img src="../../.gitbook/assets/image (9) (1).png" alt=""><figcaption></figcaption></figure>

## Afterthought

It's such a simple solution that I'm so mad that I scourge the whole source code many times over just to not realize the solution during the competition.&#x20;

Alas, it's a good experience for myself to always check on user input, what happens to the input, and what can I exploit at the input. It's obvious but sometimes I'm too stupid to remember that

## Links

Source Code:

{% embed url="https://github.com/BoredAngel/CTFs-Writeup/tree/main/2025/Compfest-17/web/basssh" %}

