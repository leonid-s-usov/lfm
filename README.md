# lfm

[![Travis](https://img.shields.io/travis/willyg302/lfm.svg?style=flat-square)](https://travis-ci.org/willyg302/lfm)
[![license](http://img.shields.io/badge/license-MIT-red.svg?style=flat-square)](https://raw.githubusercontent.com/willyg302/lfm/master/LICENSE)

> The [AWS Lambda](http://aws.amazon.com/lambda/) Function Manager

## Hi There!

You're probably wondering what lfm is good for. Well, suppose you wake up one day and suddenly realize you need a Lambda function for [AES encryption](http://en.wikipedia.org/wiki/Advanced_Encryption_Standard). You *could* roll your own solution, but ain't nobody got time for that. So you do a quick GitHub search and -- lo and behold -- there's [this beauty](https://github.com/willyg302/aws-lambda-aes).

Normally you'd have to clone the repo, install its dependencies, zip it up, and deploy it yourself. But with lfm, you can just do:

```bash
$ lfm deploy gh:willyg302/aws-lambda-aes
```

## What?! No Way!

Yup, and it works with a few other things, too:

Source | Command
--- | ---
**Git repo** | We just covered this, bro
**GitHub Gist**, [1 file](https://gist.github.com/willyg302/25b8f32e6784aca03a27) | `lfm deploy gist:willyg302/25b8f32e6784aca03a27`
**GitHub Gist**, [2+ files](https://gist.github.com/willyg302/560ab5d328b37d2cd4cc) | `lfm deploy gist:willyg302/560ab5d328b37d2cd4cc`
**Local file** | `lfm deploy awesome-sauce.js`
**Local directory** | `lfm deploy my-sweet-function/`
**Working directory** | `lfm deploy`
**S3 bucket** | `lfm deploy s3:mah-bucket`
**File on S3** | `lfm deploy s3:mah-bucket/hello-world.js`
**Directory on S3** | `lfm deploy s3:mah-bucket/my-function`
**Valid URL** | `lfm deploy http://www.my-site.com/my-function.js`

In addition, you can override any of the usual config (see `lfm deploy -h` for options).

## So What's the Secret?

Glad you asked! The magic of lfm is a special file called `.lambda.yml` at the root of a repo or directory. It looks something like this:

```yaml
config:
  FunctionName: my-awesome-sauce-function
  Handler: index.handler
  Runtime: nodejs
  Description: This function will blow your mind
  Role: execution_role_arn  # Not recommended, especially in a public repo
install: npm install --production
ignore:
  - test/
  - README.md
```

`config` holds all that junk you're used to passing to `create-function`, so you don't have to type it out any more. Note that any config you provide to `lfm deploy` will override the values in this file.

`install` is a single command for installing dependencies before zipping up the function. In this example, we want to install some Node modules so we use `npm install --production`, but you can just as well [shell out to `make`](https://gist.github.com/willyg302/c09048aeff3ae48ddcf2) for more heavy lifting.

`ignore` is a list of paths that will not be added to the zip file.

**NOTE**: You don't *need* a `.lambda.yml` to be able to use lfm; it's just easier that way. Without the config file, you'll have to provide all the required config as command-line arguments.

### But I Only Have One File...

Cool beans. Just stick that config as YAML in your front matter:

```js
/**
 * config:
 *   FunctionName: hello-world
 *   Handler: hello-world.handler
 *   Runtime: nodejs
 *   Description: A simple AWS Lambda function
 */
console.log('Loading function');

exports.handler = function(event, context) {
    console.log('value1 =', event.key1);
    console.log('value2 =', event.key2);
    console.log('value3 =', event.key3);
    context.succeed(event.key1);  // Echo back the first key value
    // context.fail('Something went wrong');
};
```

Save this in `hello-world.js` and you're good to go! It's probably worth mentioning that since you have just a single file, you won't be doing any installing or ignoring of files or anything like that.

### But Roles Are So *Annoying*...

Wish you didn't have to type the role every time? It's a bad idea to include the role in your `.lambda.yml` or front matter for security reasons, but we've got you covered with one extra layer of config:

```yaml
# Save this in ~/.aws/lambda.yml
roles:
  default: arn:aws:iam::some-role
  bunnies: arn:aws:iam::a-much-fluffier-role
```

Now you can rest those poor fingertips of yours:

```bash
$ lfm deploy awesome-sauce.js  # Will use default role
$ lfm deploy awesome-sauce.js -r bunnies  # You guessed it!
$ lfm deploy awesome-sauce.js --role arn:aws:iam::blahblah  # If you really want to...
```

## Okay, I'm Sold, Gimme!

lfm is still in early development, so don't expect to be finding it on PyPI. You can grab it with a quick `pip install git+https://github.com/willyg302/lfm.git@master`.

If, like Rust, lfm decides to [eat your laundry](https://github.com/rust-lang/rust-www/blob/f6dbd32bd9f8a450de09a816d08a5338c13d7fa5/index.html#L63), please file an issue.

## I Want Moar

Don't fret, we hear you! There are currently plans for the following features:

- **A Site**: All fancy-shmancy and such, so you can search for functions and be all social from the comfort of your browser.
- **Webhooks**: A bit far-fetched, but wouldn't it be cool to `git push` and kick off a Lambda deploy?

## Testing

Run unit tests with `python setup.py test`.

Run integration tests with `python integ`. See [`integ/__init__.py`](https://github.com/willyg302/lfm/blob/master/integ/__init__.py) for more information.
