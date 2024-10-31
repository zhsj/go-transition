<!DOCTYPE html>
<html lang="en-US">
<head>
  <title>Go Tracker</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <style>
    html {
        padding: 1em;
        margin: auto;
        line-height: 1.5;
        font-size: 1em;
    }

    body {
        text-align: center;
    }

    h1,h2,h3,h4,h5,h6 {
        margin: 1em 0 1em;
    }

    p,ul,ol {
        color: #1d1d1d;
        font-family: sans-serif;
        margin: 4px;
    }

    .update {
        font-size: .8em
    }

    table {
        table-layout: fixed;
        border-collapse: collapse;
        border: 2px solid #E95420;
    }

    th {
        background-color: #E95420;
        color: white;
    }

    td {
        text-align: center;
        border: 1px solid white;
    }

    td.current {
        background-color: #109d26;
    }

    td.nofips {
        background-color: yellow;
    }

    td.outdated {
        background-color: orange;
    }

    tbody th:nth-child(1) {
        text-align: left;
    }

    tbody th {
        font-size: 1.2em;
    }

    tbody td:nth-child(1) {
        text-align: left;
        background-color: #f0f0f0;
        font-size: 1.2em;
    }

    th, td {
        padding: .2em .5em;
    }

    td {
        border: 1px solid lightgray;
    }

    .hidden {
        font-size: .7em;
        display: block;
    }

    td:hover > .hidden {
        display: block;
    }

    .tbox {
        display: inline-block;
    }

    .tbox p {
        text-align: right;
        font-size: .8em;
        padding-right: .5em;
    }

    footer {
        text-align: center;
    }
  </style>
</head>
<body>
<div class=tbox>
<table>
  <tr>
    {{ range .UbuntuRels }}
    <th>{{ . }}</th>
    {{ end }}
  </tr>
  {{ range .UbuntuRows }}
  <tr>
    {{ range . }}
    <td>
      {{ range . }}
      <div>{{ . }}</div>
      {{ end }}
    </td>
    {{ end }}
  </tr>
  {{ end }}
</table>
<table>
  <tr>
    {{ range .DebianRels }}
    <th>{{ . }}</th>
    {{ end }}
  </tr>
  {{ range .DebianRows }}
  <tr>
    {{ range . }}
    <td>
      {{ range . }}
      <div>{{ . }}</div>
      {{ end }}
    </td>
    {{ end }}
  </tr>
  {{ end }}
</table>
<p>Last updated: {{ .Now }}</p>
</div>
</body>
</html>
