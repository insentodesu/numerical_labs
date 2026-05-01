# Деплой labs.inst.rest на свой VPS (Ubuntu/Debian)

Репозиторий клонируется целиком; на сервере ожидается путь **`/opt/labs/numerical_labs`** (см. юниты в `deploy/systemd/`).

Схема: **портал** на `/`, лабораторные на **`/lab1/`**, **`/lab2/`** и **`/lab3/`**, четыре процесса Streamlit за **Nginx**, Streamlit слушает только **127.0.0.1**.

## 1. Сервер: пакеты и пользователь

```bash
sudo apt update
sudo apt install -y python3-venv nginx git
# Для HTTPS:
sudo apt install -y certbot python3-certbot-nginx
```

```bash
sudo useradd -r -m -d /opt/labs -s /bin/bash labs 2>/dev/null || true
sudo mkdir -p /opt/labs
sudo chown labs:labs /opt/labs
```

## 2. Клонировать репозиторий

```bash
sudo -u labs git clone https://github.com/insentodesu/numerical_labs.git /opt/labs/numerical_labs
```

(Если каталог уже есть: `sudo -u labs git -C /opt/labs/numerical_labs pull`.)

## 3. Конфиги Streamlit для продакшена

```bash
sudo -u labs mkdir -p /opt/labs/numerical_labs/portal/.streamlit \
  /opt/labs/numerical_labs/lab1/.streamlit \
  /opt/labs/numerical_labs/lab2/.streamlit \
  /opt/labs/numerical_labs/lab3/.streamlit

BASE=/opt/labs/numerical_labs/portal/deploy/configs
sudo -u labs cp "$BASE/portal.config.toml" /opt/labs/numerical_labs/portal/.streamlit/config.toml
sudo -u labs cp "$BASE/lab1.config.toml"   /opt/labs/numerical_labs/lab1/.streamlit/config.toml
sudo -u labs cp "$BASE/lab2.config.toml"  /opt/labs/numerical_labs/lab2/.streamlit/config.toml
sudo -u labs cp "$BASE/lab3.config.toml"  /opt/labs/numerical_labs/lab3/.streamlit/config.toml
```

`baseUrlPath` в lab1/lab2/lab3 обязателен для прокси Nginx по `/lab1/`, `/lab2/` и `/lab3/`.

## 4. Виртуальные окружения и зависимости

```bash
sudo -u labs bash -c '
cd /opt/labs/numerical_labs/portal && python3 -m venv venv && . venv/bin/activate && pip install -U pip && pip install -r requirements.txt
cd /opt/labs/numerical_labs/lab1   && python3 -m venv venv && . venv/bin/activate && pip install -U pip && pip install -r requirements.txt
cd /opt/labs/numerical_labs/lab2   && python3 -m venv venv && . venv/bin/activate && pip install -U pip && pip install -r requirements.txt
cd /opt/labs/numerical_labs/lab3   && python3 -m venv venv && . venv/bin/activate && pip install -U pip && pip install -r requirements.txt
'
```

## 5. Systemd

```bash
sudo cp /opt/labs/numerical_labs/portal/deploy/systemd/labs-portal.service /etc/systemd/system/
sudo cp /opt/labs/numerical_labs/portal/deploy/systemd/labs-lab1.service   /etc/systemd/system/
sudo cp /opt/labs/numerical_labs/portal/deploy/systemd/labs-lab2.service   /etc/systemd/system/
sudo cp /opt/labs/numerical_labs/portal/deploy/systemd/labs-lab3.service   /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable --now labs-portal labs-lab1 labs-lab2 labs-lab3
sudo systemctl status labs-portal labs-lab1 labs-lab2 labs-lab3
```

При другом домене измените `Environment=LAB1_URL=...`, `LAB2_URL=...` и `LAB3_URL=...` в `labs-portal.service`.

## 6. Nginx

```bash
sudo cp /opt/labs/numerical_labs/portal/deploy/nginx-labs.inst.rest.conf /etc/nginx/sites-available/labs.inst.rest
sudo ln -sf /etc/nginx/sites-available/labs.inst.rest /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

В DNS для **labs.inst.rest** должен быть A/AAAA-запись на IP сервера.

### HTTPS

```bash
sudo certbot --nginx -d labs.inst.rest
```

Файрвол (**ufw**):

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
```

## 7. Проверка

- `https://labs.inst.rest/` — портал.
- Кнопки ведут на `.../lab1/`, `.../lab2/` и `.../lab3/`.
- Логи: `journalctl -u labs-portal -f`.

## Обновление кода

```bash
sudo -u labs git -C /opt/labs/numerical_labs pull
# при изменении requirements.txt — pip install в нужном venv
sudo systemctl restart labs-portal labs-lab1 labs-lab2 labs-lab3
```
