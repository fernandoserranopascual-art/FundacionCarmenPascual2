# FundacionCarmenPascual2

Sitio web de la Fundación Carmen Pascual. Arte Salud Naturaleza.

- **Publicado en:** [www.fundacioncarmenpascual.org](https://www.fundacioncarmenpascual.org)
- **Se sirve desde:** `docs/` (GitHub Pages). El dominio está en `docs/CNAME`.
- **Toda la web es una sola página:** `docs/index.html`, con las secciones
  ocultas que se despliegan al pulsar. Las subcarpetas de `docs/` guardan las
  imágenes y los textos largos.

> Cuidado: en el repositorio `FundacionCarmenPascual` hay una carpeta `docs/`
> con una copia antigua del sitio. **No se publica y no se actualiza.** La web
> buena es la de aquí.

## Convenciones de estilo

### Palabras que van siempre en mayúsculas: INCLUSIÓN y KINI

La palabra **INCLUSIÓN** se escribe siempre en mayúsculas, en español y en
inglés (**INCLUSION**), en cualquier sitio donde aparezca: títulos, programas,
pies de imagen, textos de `alt` y texto corrido.

No es un capricho tipográfico: es el nombre y el sentido de lo que hace la
Fundación, y así aparece en los carteles de las Jornadas.

Lo mismo con **KINI**, el nombre por el que se conoce a Kini Carrasco Ávila, que
en sus carteles figura siempre en mayúsculas.

En los dos casos la palabra se envuelve en `<span class="incl">`, que la deja en
mayúsculas pero a `0.86em`, de modo que su altura case con la del texto que la
rodea y no dé el salto de las mayúsculas a cuerpo completo. Donde el contenedor
ya va en mayúsculas por CSS, la regla se anula sola. Dentro de un atributo
`alt` no cabe la etiqueta: ahí la palabra va en mayúsculas y sin envolver.

```html
<h2>IV Jornada de Arte y Ciencia por la INCLUSIÓN</h2>
<h4>Deporte e INCLUSIÓN: la mística de la superación</h4>
<p>Su ejemplo fue el principio. La INCLUSIÓN de todos es el horizonte.</p>
```

Para comprobar que no se ha escapado ninguna:

```bash
grep -n "\b[Ii]nclusi[oó]n\b" docs/index.html   # no debe devolver nada
grep -n "Kini" docs/index.html              # tampoco
```

### La web es bilingüe

Cada texto va duplicado con las clases `only-es` y `only-en`. Al añadir
contenido hay que escribir **las dos versiones**; si no, ese texto desaparece
al cambiar de idioma. Para comprobar que están equilibradas:

```bash
grep -c "only-es" docs/index.html
grep -c "only-en" docs/index.html
```

### Imágenes

Se reducen a **1600 px de ancho**, JPEG de calidad 82, progresivo. Los
carteles A3 originales pesan entre 2 y 3,5 MB; así se quedan en 300-650 KB.

### La Fundación está en trámite de inscripción

Hasta que se resuelva el expediente del Registro de Fundaciones de competencia
estatal, donde se cite a la Fundación como organizadora debe figurar la nota de
que está **pendiente de inscripción**, como hacen los carteles.

### Patrocinadores

Solo se nombra a quien ha comprometido su apoyo. Si un patrocinio se aplaza o
queda en el aire, se retira de la web hasta que se confirme.
