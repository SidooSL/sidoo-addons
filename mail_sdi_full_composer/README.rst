=======================
Mail SDI Full Composer
=======================

Proposito
=========

Este modulo hace que el boton Enviar Mensaje del chatter abra directamente el
compositor completo de correo en lugar del editor inline.

Enfoque
=======

La implementacion aplica un patch frontend minimo sobre el chatter de Odoo y
reutiliza el wizard estandar ``mail.compose.message``.

Dependencias
============

* mail
