Apptainer is the only requirement to run Ribbon. Install apptainer for your system [here](https://apptainer.org/docs/admin/main/installation.html#install-ubuntu-packages).

We recommend creating a fresh environment for Ribbon:
```bash
conda create --name ribbon python=3.12 -y
conda activate ribbon
```

Then, install Ribbon in a clean python environment:
```bash
pip install ribbon-toolkit
```