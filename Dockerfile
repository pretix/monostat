FROM python:3.12-bookworm

RUN apt-get update && apt-get install -y git gettext \
	libpq-dev locales build-essential sudo nginx supervisor \
	--no-install-recommends && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* && \
    dpkg-reconfigure locales && \
	locale-gen C.UTF-8 && \
	/usr/sbin/update-locale LANG=C.UTF-8 && \
    useradd -ms /bin/bash -d /src -u 15372 monostat && \
    echo 'monostat ALL=(ALL) NOPASSWD:SETENV: /usr/bin/supervisord' >> /etc/sudoers && \
    mkdir /etc/supervisord

ENV LC_ALL C.UTF-8
ENV DJANGO_SETTINGS_MODULE=monostat.settings
ENV MONOSTAT_DATA_DIR /data

COPY docker/monostat.bash /usr/local/bin/monostat
COPY docker/supervisord /etc/supervisord
COPY docker/supervisord.all.conf /etc/supervisord.all.conf
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY pyproject.toml /src/pyproject.toml
COPY manage.py /src/manage.py
COPY monostat /src/monostat

RUN mkdir /static && \
    cd /src && \
    pip3 install -U pip setuptools wheel && \
    pip3 install . gunicorn && \
    pwd && \
    ls -lisah * && \
    DJANGO_SETTINGS_MODULE=monostat.settings python3 -m monostat collectstatic --noinput && \
    chmod +x /usr/local/bin/monostat

RUN mkdir /data
VOLUME /data

EXPOSE 80
USER monostat
ENTRYPOINT ["/usr/local/bin/monostat"]
CMD ["web"]
