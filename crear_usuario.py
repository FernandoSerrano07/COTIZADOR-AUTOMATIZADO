from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")
from database import SessionLocal, engine
import models
from passlib.context import CryptContext

# Esto crea las tablas automáticamente en MySQL si no existen
models.Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = SessionLocal()

# Datos de tu usuario
usuario_nuevo = "cotizador"
password_nuevo = "123456"

hashed_pwd = pwd_context.hash(password_nuevo)
nuevo_usuario = models.User(username=usuario_nuevo, hashed_password=hashed_pwd)

db.add(nuevo_usuario)
db.commit()
db.close()
print("¡Tabla creada y usuario registrado en MySQL con éxito!")