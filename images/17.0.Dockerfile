FROM ubuntu:22.04

ENV LANG C.UTF-8

RUN useradd odoo

RUN mkdir -p /home/odoo

RUN chown -R odoo:odoo /home/odoo

RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive \
apt-get install -y --no-install-recommends \
python3 \
python3-pip \
python3-venv \
python3-dev \
python-is-python3 \
build-essential \
fonts-dejavu-core \
fonts-freefont-ttf \
fonts-freefont-otf \
fonts-noto-core \
fonts-inconsolata \
fonts-font-awesome \
fonts-roboto-unhinted \
gsfonts \
libjs-underscore \
lsb-base \
postgresql-client \
xz-utils \
npm \
node-less \
curl \
wkhtmltopdf \
libpq-dev \
libldap2-dev \
libsasl2-dev

RUN python -m venv /home/odoo/odoo-venv

# TODO: Use below for tagged releases
# COPY files/requirements.17.0.txt /home/odoo/odoo-requirements.txt
# Use below in build to generate a locked requirements to update files/requirements.x.txt
# RUN pip install --no-cache-dir pip-tools
# RUN pip-compile -o /home/odoo/odoo-requirements.lock.txt --all-extras --dry-run /home/odoo/odoo-requirements.txt

# Get requirements.txt rolling
RUN curl https://raw.githubusercontent.com/odoo/odoo/17.0/requirements.txt > /home/odoo/odoo-requirements.txt

RUN /home/odoo/odoo-venv/bin/pip install --no-cache-dir debugpy -r /home/odoo/odoo-requirements.txt

# support for multilingual fonts
RUN npm install -g rtlcss@4.3.0

USER odoo

WORKDIR /home/odoo

