# Running IPBDB locally (Windows, development)

Same stack as ACol: **Django 2.2**, which runs on **Python 3.9** only, **MariaDB**,
and `vamdctap` from `../NodeSoftware`.

## Setup, done once

1. Database from the dump:
   ```powershell
   & "C:\Program Files\MariaDB 12.3\bin\mysql.exe" -u root -p -e "DROP DATABASE IF EXISTS ipbdb; CREATE DATABASE ipbdb CHARACTER SET utf8mb4;"
   cmd /c '"C:\Program Files\MariaDB 12.3\bin\mysql.exe" -u root -p ipbdb < ..\ipbdb_<date>.sql'
   ```

2. `local_settings.py`, not committed. It overrides the database, the template and
   static paths, the log file, and sets `MIGRATION_MODULES = {'node': None}`.
   The last one matters: `node/migrations/*` are old **South** migrations that
   Django 2.2 cannot import (`ModuleNotFoundError: No module named 'south'`), and
   the schema is already in the dump.

3. Contrib migrations. The dump carries tables from the Django 1.x era and has no
   `django_migrations` table, so runserver reports 19 unapplied migrations. This is
   not harmless: `auth_user.username` was `varchar(30)`, `email` `varchar(75)` and
   `last_login` was NOT NULL, which breaks the admin on Django 2.2. Fix, applied once:
   ```powershell
   ..\acol\.venv\Scripts\python.exe manage.py migrate --fake-initial
   ```
   Node data is untouched. A copy of the database before this step is kept as
   `ipbdb_backup`.

4. Virtual environment: the existing `..\acol\.venv` is reused. It has Python 3.9,
   Django 2.2.8, mysqlclient, and a `nodesoftware.pth` file that puts
   `..\NodeSoftware` on the path, so `vamdctap` can be imported.

## Running

```powershell
cd <checkout>\ipbdb
..\acol\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001
```

Port 8001 so that ACol can stay on 8000.

- Site:      http://127.0.0.1:8001/
- Admin:     http://127.0.0.1:8001/admin/
- Data sets: http://127.0.0.1:8001/plots/
- TAP:       http://127.0.0.1:8001/tap/capabilities

The database holds 100 collisions, 217 tabulated data sets, 733 datalists and
45 species.

## Plots

`node/plotting.py` decides the plot type from the shape of the data, nothing is
entered by hand:

| kind | condition | plot |
|---|---|---|
| `surface` | several energies, all with the same angles | 3D surface DCS(E, theta) |
| `waterfall` | several energies with different angles | 3D lines, no interpolation |
| `curve_theta` | a single energy | 2D curve DCS(theta) |
| `curve_e` | no angle axis | 2D curve sigma(E) |
| `invalid` | axis lengths do not match | nothing, the problems are listed |

Current counts: 72 waterfall, 67 surface, 60 curve_e, 10 invalid, 8 curve_theta.

Pages:

- `/plots/` list of all sets, filter by plot type and by target
- `/plots/<id>/` one plot, with 3D, 2D and log scale buttons
- `/plots/<id>/data.json` and `/plots/<id>/data.csv` the same set as data

Plotly is served from `static/js/plotly.min.js`, version 2.35.3, so the node does
not depend on a CDN.

## Search page

The page itself is unchanged. Three small differences:

1. `combo-ajax.js` is replaced by the local `static/js/beamdb-search.js`. The
   original has `base_url` fixed to `http://servo.aob.rs/emol`, so the local page
   was searching the production node. The logic is the same.
2. A short table above the XML shows what was found, with links to the plot and to
   the CSV. It is filled from `/search_results/`.
3. The XSAMS output is still rendered by XMLDisplay at the bottom of the page.

The TAP service is untouched.
