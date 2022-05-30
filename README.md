# Test Data Simulation

This repository contains two programs for test data simulation given as a data science project. These two programs can be used independently and were made to expedite test data generation and manipulation for product fail-state testing.

`generatetestdata.py` focuses on chat/text generation and augmentation. Data is pulled from `data/` depending on the Smarsh Scenario chosen, or from a user inputted file.

### Suggested Usage of `generatetestdata.py`
#### Available Parameters:
```
scenario | numdata | inputfile | custom | labelcase | labeled | augment | randsamp
```
| Parameters    | Description                                                       | Example            |
| ------------- | ----------------------------------------------------------------- | ------------------ |
| --scenario    | specifies which available scenario to use for generation          | `--scenario="cov"` |
| --numdata     | specifies how many entries to create                              | `--numdata=50`     |
| --inputfile   | user inputted file to use for generation/augmentation             | `--inputfile="data/example_file.csv"`
| --custom      | user inputted text primarily for simple augmentation              | `--custom="Don't tell anyone"`
| --labelcase   | specifies if output should contain only positive or negative hits | `--labelcase=0`
| -l --labeled  | will output the respective label alongside the ouputted text      |
| -a --augment  | will augment the text output with the provided augmenter          |
| -r --randsamp | will pull a random sample of text from either an existing scenario or user provided file|

`generateemaildata.py` focuses on email generation, manipulation, and augmentation. Data is pulled from `data/` is a Smarsh Scenario is specified as an input file, a user inputted file, or user specified arguments.

### Suggested Usage of `generateemaildata.py`
#### Available Parameters:
```
subject | sender | recipients | cc_recipients | bcc_recipients | body | attachments | lang | charset
```
```
numdata | inputfile | labelcase | augment | custom | reply | thread
```
| Parameters       | Description                                     | Example            |
| ---------------- | ----------------------------------------------- | ------------------ |
| --subject        | defines the subject of the email                | `--subject="Lorem Ipsum"`
| --sender         | defines the sender of the email                 | `--sender="sender@smarsh.com"`
| --recipients     | defines the recipeint(s) of the email           | `--recipients test@smarsh.com test2@gmail.com`
| --cc_recipients  | defines the cc_recipeint(s) of the email        | `--cc_recipients cc_one@test.com cc_two@test.com`
| --bcc_recipients | defines the bcc_recipeint(s) of the email       | `--bcc_recipients bcc_one@test.com bcc_two@test.com`
| --body           | defines the body of the email                   | `--body="Lorem ipsum dolor sit amet"`
| --attachments    | user inputted attachements for the email        | `--attachments="data/sample1;data/sample2"`
| --lang           | defines the language in the header of the email | `--lang="en"`
| --charset        | defines the charset in the header of the email  | `--charset="utf-8"`
| --numdata        | specifies how many .eml files to create         | `--numdata=5`
| --inputfile      | user inputted file to use for email body        | `--inputfile="data/sampledata.csv"`
| --labelcase      | specifies if output should contain only positive or negative hits | `--labelcase="1"`
| -a --augment     | will augment the text output with the provided augmenter
| -c --custom      | using this tag will allow for custom .eml creation
| -r --reply       | will generate an email reply chain
| -t --thread      | will generate a thread of randomly selected emails

