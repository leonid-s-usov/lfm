# lfm

[![Travis](https://img.shields.io/travis/willyg302/lfm.svg?style=flat-square)](https://travis-ci.org/willyg302/lfm)
[![license](http://img.shields.io/badge/license-MIT-red.svg?style=flat-square)](https://raw.githubusercontent.com/willyg302/lfm/master/LICENSE)

> The [AWS Lambda](http://aws.amazon.com/lambda/) Function Manager

## Hi There!

You're probably wondering what lfm is good for. Well, suppose you wake up one day and suddenly realize you need a Lambda function for [AES encryption](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard). You *could* roll your own solution, but ain't nobody got time for that. So you do a quick GitHub search and -- lo and behold -- there's [this beauty](https://github.com/willyg302/aws-lambda-aes).

Normally you'd have to clone the repo, install its dependencies, zip it up, and deploy it yourself. But with lfm, you can just do:

```bash
$ lfm deploy gh:willyg302/aws-lambda-aes --role execution_role_arn
```

## What?! No Way!

Yup, and it works with local directories too:

```bash
$ lfm deploy my-sweet-function/ --role execution_role_arn
$ lfm deploy --role execution_role_arn  # Will deploy working directory
```

Only got a single file? No problemo:

```bash
$ lfm deploy awesome-sauce.js --role execution_role_arn
```

You can even deploy straight from GitHub Gists:

```bash
$ lfm deploy gist:willyg302/560ab5d328b37d2cd4cc --role execution_role_arn
```

If you haven't already guessed by now, your Gist can be a [single file](https://gist.github.com/willyg302/25b8f32e6784aca03a27) or [multiple files](https://gist.github.com/willyg302/560ab5d328b37d2cd4cc).

In addition, you can override any of the usual config (see `lfm deploy -h` for options).

## So What's the Secret?

The magic of lfm is a special file called `.lambda.yml` at the root of a repo or directory. It looks something like this:

```yaml
config:
  FunctionName: my-awesome-sauce-function
  Handler: index.handler
  Mode: event
  Runtime: nodejs
  Description: This function will blow your mind
  Role: execution_role_arn  # Not recommended, especially in a public repo
install: npm install --production
ignore:
  - test/
  - README.md
```

`config` holds all that junk you're used to passing to `upload-function`, so you don't have to type it out any more. Note that any config you provide to `lfm deploy` will override the values in this file.

`install` is a single command for installing dependencies before zipping up the function. In this example, we want to install some Node modules so we use `npm install --production`, but you can just as well shell out to `make` for more heavy lifting.

`ignore` is a list of paths that will not be added to the zip file.

**NOTE**: You don't *need* a `.lambda.yml` to be able to use lfm; it's just easier that way. Without the config file, you'll have to provide all the required config as command-line arguments.

### But I Only Have One File...

Cool beans. Just stick that config as YAML in your front matter:

```js
/**
 * FunctionName: hello-world
 * Handler: hello-world.handler
 * Mode: event
 * Runtime: nodejs
 * Description: My awesome Hello World function!
 */
console.log('Loading event');

exports.handler = function(event, context) {
    console.log("value1 = " + event.key1);
    console.log("value2 = " + event.key2);
    console.log("value3 = " + event.key3);
    context.done(null, "Hello World");
};
```

Save this in `hello-world.js` and you're good to go! It's probably worth mentioning that since you have just a single file, you won't be doing any installing or ignoring of files or anything like that. So the only stuff that goes in the YAML is what you'd pass to `upload-function`.

## Okay, I'm Sold, Gimme!

lfm is still in early development, so don't expect to be finding it on PyPI. You can grab it with a quick `pip install git+https://github.com/willyg302/lfm.git@master`.

If, like Rust, lfm decides to [eat your laundry](https://github.com/rust-lang/rust-www/blob/f6dbd32bd9f8a450de09a816d08a5338c13d7fa5/index.html#L63), please file an issue.

## I Want Moar

Don't fret, we hear you! There are currently plans for the following features:

- **Webhooks**: A bit far-fetched, but wouldn't it be cool to `git push` and kick off a Lambda deploy?

## Testing

Call tests with `python setup.py test`.
