# Python Package Template

This is a template for python packages which can be pushed to Sensirion's PyPi
server at https://pypi.sensirion.lokal/.


This [README.md](README.md) contains information for contributors of the
project. The package description (which is shown on
[PyPi](https://pypi.sensirion.lokal/)) is located in [README.rst](README.rst).

---

### Naming convention

At Sensirion the following naming convention for the packages is used:

* Package names must be all lowercase and words separated by hyphens (e.g.
  `package-name`). The name is defined in `setup.py` and is used for
  `pip install`.
* In addition, all Sensirion packages (customer and internal) must start with
  `sensirion-` (e.g. `sensirion-shdlc-driver`).
* The package directory must be named equal to the package name in `setup.py`,
  but all hyphens replaced by underscores (e.g. `sensirion_shdlc_driver`). This
  is the name for importing the package.
* The project at GitLab must be named like the package name, but with the prefix
  `python-` instead of `sensirion-` (e.g. `python-shdlc-driver`, **not**
  `sensirion-shdlc-driver` or `python-sensirion-shdlc-driver`).

In this template, following placeholders are used to show where to place the
package name in which variant:
* `<sensirion-package-name>`: Regular package name with hyphens (e.g.
  `sensirion-shdlc-driver`)
* `<sensirion_package_name>`: Package name with underscores (e.g.
  `sensirion_shdlc_driver`)


### Checklist for a new package

1. Create a new project in Gitlab. Please follow the naming convention as
  explained above (e.g. `python-shdlc-driver`).
2. Clone the project into a folder
3. Add the content of this template, modifying the following:
   * Fill `README.rst` (replace three placeholders with the package name)
   * Adapt this `README.md` (remove everything you don't need)
   * Rename the `sensirion_package_name` folder to your package's name (e.g.
     `sensirion_shdlc_driver`)
   * In `setup.cfg`, replace `<sensirion_package_name>` with the package's name
   * Enter the desired version number to `sensirion_package_name/version.py`
4. Configure your `setup.py`:
   * Insert the package name
   * Add your name and email
   * Add a short package description
5. Configure the CI
   * Rename the file `.gitlab-ci.yml.template` to `.gitlab-ci.yml`
6. Configure the docs
   * Open the file `docs/conf.py` and change `<sensirion_package_name>` to
   reflect your package name.
   * By default the documentation only contains an example. Read
   __Document your code__ further down to see how you can
   write meaningful documentation.
7. Push everything as initial commit to your GitLab project
8. Start coding ;-)


### Notes

* After the first release it is mandatory to include all changes to the
  changelog in `CHANGELOG.rst`.
* A relatively strict testing is automatically configured:
  * The folder `tests` is meant for unit and integration test. We use
    [pytest](https://docs.pytest.org) for this purpose.
    * Per default, an import test [tests/test_import.py](tests/test_imports.py)
      is active. It tests all modules which are included in the package.
      Exceptions can be defined via regular expression in the `EXCLUDES`
      variable.
    * It is highly recommended to add further tests.
    * To run all tests, you can execute `pytest` in the root of the package. To
      run all tests in a single file, you can run `pytest <FILENAME>`. To run a
      single test, you can run `pytest <FILE>::<FUNCTION>`. In PyCharm you can
      right-click on the function name and select 'Run py.test for FUNCTION'.
    * PyTest also measures the code coverage of the tests, and outputs how much
      of each file the tests have executed. We do not require a minimum coverage
      to consider the tests successful, but it is good practice to seek to
      improve this number.
  * We use `flake8` for static syntax checks. If a particular tests fails but
    you really need to keep the code as is, you can add an exception by adding a
    comment to the conflicting line. An example can be found in
    `sensirion_package_name/__init__.py`. Here `flake8` would raise the F401
    Error, complaining of an unused import. As this import is needed, albeit not
    used in the package itself, we flag it with `# noqa: F401`. For more
    details, please consult the
    [flake8 documentation](http://flake8.pycqa.org/en/latest/user/violations.html#in-line-ignoring-errors)
  * All files in the repository are checked with
    [editorconfig-checker](https://editorconfig-checker.github.io/) to enforce
    consistent line endings, trailing spaces etc. If the CI job
    `check_editorconfig` fails, check its output to see what you need to fix.
    If you need to change the configuration (or disable a check) for specific
    files, add new rules to the `.editorconfig` file. For details, please take
    a look at the [EditorConfig documentation](https://editorconfig.org/).


### Document your code

It is relatively easy to document your code and generate a documentation in
html.
* We use Sphinx to generate the documentation. If you want to read all about
  it go to the [Sphinx Web Page](https://www.sphinx-doc.org/en/master/usage/quickstart.html#defining-document-structure)
* There is a folder called docs. Inside you find two files of interest:
  * `index.rst`:

    Here you define the structure of your Documentation by defining a table of
    contents (TOC). It is also the start page of your documentation if you
    host it on the web. In the TOC you define which files should be part of
    your documentation. You can include any file in the `docs/` folder that
    ends in .rst. There is already one file included which is called `api.rst`.
    Have a look at `docs/index.rst` to learn more.

  * `api.rst`

    This file is intended to host your packages application programming
    interface, short API. You can auto-generate api from the docstrings in
    your package. Open `docs/api.rst` to learn more.
* Gitlab will automatically build your docs on every commit. Just browse the
  artifacts of the build job called `build_docs_v1` for the file
  `docs/_build/html/index.html` to see the results. If you add a tag to your
  project gitlab will deploy it to the gitlab page of your project.
  * Once it has been deployed to pages you can find the url of your gitlab
    pages on your gitlab project under __Settings > Pages__.
* If you want to try and build your documentation locally on your machine you'll
  need to first install the requirements. Open a console in the project folder
  (where setup.py is located) with your projects virtualenv activated and run
  the following code:
  ```bash
  pip install -e .[docs]
  ```
  Then change to the `docs/` folder and run

  ```bash
  make html
  ```
  This should work on Mac, Linux and Windows and will produce a new folder
  `docs/_build/html` in which you will find a lot of files. Try opening
  `docs/_build/html/index.html` with your browser to see the results.
