---
description: '[Solved] A white box web exploitation CTF challenge from WreckIT 2025'
---

# \[Web] Safe Template

## TL;DR

* We have a website that has SSTI but with big blacklist: no dangerous keyword like config, import; the usual.
* \[], '", % is not blacklist so we can bypass any keyword blacklist, () is not blacklisted so we can call function, \[digit] is blacklisted but can be bypassed using hex like so \[0x1].
* Just make a typical payload using the above bypass.
* Profit

Flag: WRECKIT60{SSTI?\_ululala\_88efdbcc98eefdacea1344}

## Description

<figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure>

## Overview

<figure><img src="../../.gitbook/assets/image (15).png" alt=""><figcaption></figcaption></figure>

We are given a website that takes an input and then renders it in the website.&#x20;

Looking at the source code,









## Solution

exploits and steps to get the flags

## Afterthought \[OPTIONAL]

just your thoughts or comments on the challenge it self

## Links

* POC : github link
* references that might be helpful
