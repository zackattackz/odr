FROM ubuntu:22.04

ENV LANG C.UTF-8

COPY files/odoo /bin/odoo

RUN mkdir /root/src

RUN apt-get update && \
DEBIAN_FRONTEND=noninteractive \
apt-get install -y --no-install-recommends \
python3 \
python-is-python3 \
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
pgcli \
python3-babel \
python3-chardet \
python3-dateutil \
python3-decorator \
python3-docutils \
python3-freezegun \
python3-pil \
python3-jinja2 \
python3-libsass \
python3-lxml \
python3-num2words \
python3-ofxparse \
python3-passlib \
python3-polib \
python3-psutil \
python3-psycopg2 \
python3-pydot \
python3-openssl \
python3-pypdf2 \
python3-qrcode \
python3-renderpm \
python3-reportlab \
python3-requests \
python3-stdnum \
python3-tz \
python3-vobject \
python3-werkzeug \
python3-xlsxwriter \
python3-xlrd \
python3-zeep \
python3-ldap \
python3-magic \
python3-odf \
python3-pdfminer \
python3-phonenumbers \
python3-pyldap \
python3-slugify \
python3-watchdog \
python3-xlwt

RUN npm install -g rtlcss

EXPOSE 8069 8569
