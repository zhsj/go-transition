package main

import (
	"database/sql"
	"html/template"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
)

const (
	query = `
select r1.source as source, r1.package as package, r1.arch as arch, r1.version as testing_ver, r2.version as sid_ver from
(
  select p1.package as package, p1.source as source, p1.version as version, p1.architecture as arch
  from packages as p1 join sources as s1 on (
    p1.source = s1.source and p1.release = s1.release and p1.source_version = s1.version
  )
  where s1.extra_source_only is null and (
    s1.build_depends like '%golang%' or s1.build_depends_indep like '%golang%' or s1.build_depends_arch like '%golang%'
  )  and s1.release ='trixie'
) as r1 join
(
  select p2.package as package, p2.source as source, p2.version as version, p2.architecture as arch
  from packages as p2 join sources as s2 on (
    p2.source = s2.source and p2.release = s2.release and p2.source_version = s2.version
  )
  where s2.extra_source_only is null and (
    s2.build_depends like '%golang%' or s2.build_depends_indep like '%golang%' or s2.build_depends_arch like '%golang%'
  )  and s2.release ='sid'
) as r2 on (
  r1.package = r2.package and r1.source = r2.source and r1.arch = r2.arch
) where (
  r1.version != r2.version
) order by source, package, arch
`
)

var (
	tpl = template.Must(template.New("tpl").Parse(
		`<table>
  <tr>
    <th>Source</th>
    <th>Package</th>
    <th>Arch</th>
    <th>Testing Version</th>
    <th>Sid Version</th>
  </tr>
{{ range .Items }}
  <tr>
    <td><a href="https://tracker.debian.org/pkg/{{ .Source }}">{{ .Source }}</a></td>
    <td>{{ .Package }}</td>
    <td>{{ .Arch }}</td>
    <td>{{ .TestingVer }}</td>
    <td>{{ .SidVer }}</td>
  </tr>
{{ end }}
</table>

Generated by <a href="https://github.com/zhsj/go-transition/tree/master/out-of-sync">an UDD SQL</a> on {{ .Now }}.
`,
	))
)

type Result struct {
	Source     string
	Package    string
	Arch       string
	TestingVer string
	SidVer     string
}

func main() {
	db, err := sql.Open("postgres", "postgresql://udd-mirror:udd-mirror@udd-mirror.debian.net/udd")
	if err != nil {
		log.Fatal(err)
	}
	rows, err := db.Query(query)
	if err != nil {
		log.Fatal(err)
	}
	results := struct {
		Items []Result
		Now   time.Time
	}{}
	defer rows.Close()
	for rows.Next() {
		var source, pkg, arch, testingVer, sidVer string
		if err := rows.Scan(&source, &pkg, &arch, &testingVer, &sidVer); err != nil {
			log.Fatal(err)
		}
		results.Items = append(results.Items, Result{
			Source:     source,
			Package:    pkg,
			Arch:       arch,
			TestingVer: testingVer,
			SidVer:     sidVer,
		})
	}
	f, err := os.Create("out-of-sync.html")
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	results.Now = time.Now().Truncate(time.Second)
	if err := tpl.Execute(f, &results); err != nil {
		log.Fatal(err)
	}
}
