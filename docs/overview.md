Overview
========

DynDesign is a set of tools for Python developers that employs a novel strategy
when it comes to implementing design patterns; it enables developers to merge
classes on the fly as though they were working with dictionaries. By doing so,
DynDesign strives to follow several software engineering principles such as the
Single Responsibility and Open-Closed Principles from the **SOLID** acronym,
along with the **DRY** and **KISS** concepts.

The most used tools are:

- `mergeclasses`, an API to merge two or more classes;
- a set of tools to dynamically invoke methods or decorators at runtime, such as
  `decoratewith`;
- `SingletonMeta` metaclass, that can be used to implement a dynamic class builder.

<br/>
