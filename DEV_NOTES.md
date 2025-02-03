## A Note on Organization

pip requires a folder/package to install. 

Repository Name: dc-mailer
  - Uses dashes (-) as allowed in GitHub repository names.
  - Cannot be used as a Python package name due to dashes.
  - Has no effect on Python package imports.
  - Nice if it matches the PyPi distribution name.
  - The PyPi distribution name is the package/project/folder name but with a dash not underscore, because Python I guess. 
  

Package (Folder) Name: dc_mailer
  - Uses underscores (_) to ensure compatibility with Python imports.
  - Becomes an installable package when  __init__.py file is added.

File Name: emailer.py
  - The file name with a .py extension.
  - Can be executed as a script. 
  - We avoid using the file name in imports if we set up __init__.py correctly. 

pyproject.toml
  - [project] name = "dc_mailer"`
  - Used for installation (`pip install dc_mailer`).
  - The package folder should match.

```toml
[project]
name = "dc_mailer" # install name

version = "0.1.0"

[tool.setuptools]
packages = ["dc_mailer"] # list of package folders
```

## Versioning notes

- update pyproject.toml to new version, e.g., v0.1.1
- if didn't succeed, remove locally and remote first
```
git tag -d v0.1.1
git push origin --delete v0.1.1

git add .
git commit -m "bump to v0.1.1"
git tag -a v0.1.1 -m "Release v0.1.1"
git push origin main
git push origin v0.1.1
```