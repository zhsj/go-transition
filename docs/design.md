# Transition Report for Debian Go Package

## Database

| bin_pkg   | arch  | suite   | version        | built_using        | built_using_version |
| --------- | ----- | ------- | -------------- | ------------------ | ------------------- |
| go-md2man | amd64 | testing | 1.0.8+ds-1+b10 | golang-1.11        | 1.11.5-1            |
| go-md2man | amd64 | testing | 1.0.8+ds-1+b10 | golang-blackfriday | 1.5.2-1             |

| src_pkg            | suite   | version  |
| ------------------ | ------- | -------- |
| golang-1.11        | testing | 1.11.6-1 |
| golang-blackfriday | testing | 1.5.2-1  |

## Report

```
                   | amd64 arm64 armel armhf i386 mips mips64el mipsel ppc64el s390x
src_pkg (version)  |
  |                |
  +- pkg (version) | x     x     x     x     x    x    x        x      x       x
```

```
                                | amd64
golang-1.11 (1.11.6-1)          |
  |                             |
  +- go-md2man (1.0.8+ds-1+b10) | X

golang-blackfriday (1.5.2-1)    |
  |                             |
  +- go-md2man (1.0.8+ds-1+b10) | ✓
```
