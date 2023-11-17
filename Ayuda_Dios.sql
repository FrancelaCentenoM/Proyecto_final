CREATE TABLE users (
  id integer PRIMARY KEY,
  username varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
  carrera_id integer
);

CREATE TABLE horario (
  id integer PRIMARY KEY,
  materia varchar(255) NOT NULL,
  hora varchar(255) NOT NULL,
  user_id integer NOT NULL
);

CREATE TABLE anotaciones (
  id integer PRIMARY KEY,
  titulo varchar(255) NOT NULL,
  contenido varchar(255) NOT NULL,
  user_id integer NOT NULL
);

CREATE TABLE calificaciones (
  id integer PRIMARY KEY,
  user_id integer NOT NULL,
  calificacion float NOT NULL,
  materia varchar(255) NOT NULL
);

CREATE TABLE `materias` (
  `id` integer PRIMARY KEY,
  `clase_nombre` varchar(255),
  `carrera_id` integer,
  `semestre` varchar(255)
);

CREATE TABLE `carreras` (
  `id` integer PRIMARY KEY,
  `carrera_nombre` varchar(255)
);

CREATE TABLE `tareas` (
  `id` integer PRIMARY KEY,
  `descripcion` varchar(255),
  `titulo` varchar(255),
  `estado` bool,
  `user_id` integer
);


CREATE TABLE tasks (
  id INTEGER PRIMARY KEY, 
  content varchar(255) NOT NULL, 
  user_id INTEGER NOT NULL, 
  completed INTEGER DEFAULT 0
  );


CREATE TABLE calificaciones (
id INTEGER PRIMARY KEY,
 materia_id INTEGER NOT NULL,
 calificacion float NOT NULL,
 user_id INTEGER NOT NULL,
  FOREIGN KEY(materia_id) REFERENCES horario(id), 
  FOREIGN KEY(user_id) REFERENCES users(id)
  );


CREATE TABLE Horario (
    id integer PRIMARY KEY,
    dia_semana VARCHAR(15) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    materia VARCHAR(50) NOT NULL,
    user_id integer NOT NULL
);

