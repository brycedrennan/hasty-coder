# HastyCoder 🤖📝💻🚀💥

**Move Really Fast and Break Lots of Things!**

HastyCoder is your AI careless coding companion. Hasty writes entire software projects based on your single sentence 
description.

Is it a good idea to use HastyCoder? Probably not. But you're gonna anyway aren't you..

## Quick Start
You need to have an [openai](https://beta.openai.com/signup) account [api key](https://beta.openai.com/account/api-keys).
```bash
$ pip install hasty-coder
$ EXPORT OPENAI_API_KEY=<your-openai-api-key>
$ cd ~/projects
$ hasty-code "a flask app that creates funny poems using the openai client library"
# magic happens...
Project 'Poemazing' created at ~/projects/poemazing
```

**Is thinking of ideas too hard? Typing `hasty-code` too many charaters? We got you covered!**


```bash
$ hc YOLO!!!
YOLO! 😎🤘🏼👊
Yolo Idea: "A program to help procrastinators avoid getting anything done -- the ultimate 'Not-To-Do' list!"
Project 'ProcrastinatorsJaunt' created at ~/projects/procrastinators-jaunt

```

## But wait, there's more!

Hasty isn't dangerous for every task! He can add docstrings to all your python functions. 
```bash
$ hasty-code add-python-docstrings ./my-project
Found 59 code snippets in need of docstrings...
```