package main

import (
	"database/sql"
	"html/template"
	"log"
	"os"
	"strings"
	"time"

	_ "github.com/lib/pq"
)

const query = `
select * from (
  (
    select source, distribution, release, version from sources where source similar to 'golang-1.[0-9]+' and extra_source_only is null
  )
  union
  (
    select source, distribution, release, version from ubuntu_sources where source similar to 'golang-1.[0-9]+' and extra_source_only is null
  )
) as src
order by to_number(replace(source, 'golang-1.', ''), '99') desc , distribution, release
`

var UbuntuReleases = []string{
	"Plucky", "Oracular", "Noble", "Jammy", "Focal", "Bionic", "Xenial",
}

var DebianReleases = []string{
	"Sid", "Trixie", "Bookworm", "Bullseye", "Buster",
}

type Result struct {
	Source  string
	Dist    string
	Release string
	Version string
}

type Render struct {
	Now        time.Time
	UbuntuRels []string
	UbuntuRows [][][]string
	DebianRels []string
	DebianRows [][][]string
}

func main() {
	tpl := template.Must(template.New("index.tpl").ParseFiles("index.tpl"))

	f, err := os.Create("index.html")
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	render := Render{
		Now: time.Now().Truncate(time.Second),
	}
	render.UbuntuRels = append([]string{"Package"}, UbuntuReleases...)
	render.DebianRels = append([]string{"Package"}, DebianReleases...)

	db, err := sql.Open("postgres", "postgresql://udd-mirror:udd-mirror@udd-mirror.debian.net/udd")
	if err != nil {
		log.Fatal(err)
	}
	rows, err := db.Query(query)
	if err != nil {
		log.Fatal(err)
	}
	defer rows.Close()

	results := [][]Result{}
	idx := -1
	var oldSource string

	for rows.Next() {
		var source, dist, release, version string
		if err := rows.Scan(&source, &dist, &release, &version); err != nil {
			log.Fatal(err)
		}

		if source != oldSource {
			results = append(results, []Result{})
			oldSource = source
			idx += 1
		}

		results[idx] = append(results[idx], Result{
			Source:  source,
			Dist:    dist,
			Release: release,
			Version: version,
		})
	}

	for _, pkgResults := range results {
		rel2vers := map[string][]string{}
		ubuntuRow := [][]string{}
		debianRow := [][]string{}
		for _, result := range pkgResults {
			if len(ubuntuRow) == 0 {
				ubuntuRow = append(ubuntuRow, []string{result.Source})
			}
			if len(debianRow) == 0 {
				debianRow = append(debianRow, []string{result.Source})
			}
			rel := strings.Split(result.Release, "-")[0]
			ver := result.Version
			if rel != result.Release {
				ver = result.Version + "(" + strings.SplitN(result.Release, "-", 2)[1] + ")"
			}
			log.Printf("rel %s ver %v\n", rel, ver)
			rel2vers[rel] = append(rel2vers[rel], ver)
		}

		foundUbuntu := false
		foundDebian := false
		for _, ubuntuRel := range UbuntuReleases {
			row := rel2vers[strings.ToLower(ubuntuRel)]
			if len(row) != 0 {
				foundUbuntu = true
			}
			ubuntuRow = append(ubuntuRow, row)
		}
		for _, debianRel := range DebianReleases {
			row := rel2vers[strings.ToLower(debianRel)]
			if len(row) != 0 {
				foundDebian = true
			}
			debianRow = append(debianRow, row)
		}

		if foundUbuntu {
			render.UbuntuRows = append(render.UbuntuRows, ubuntuRow)
		}
		if foundDebian {
			render.DebianRows = append(render.DebianRows, debianRow)
		}

		log.Printf("ubuntu %#v\n\n", ubuntuRow)
		log.Printf("debian %#v\n\n", debianRow)
	}

	if err := tpl.Execute(f, &render); err != nil {
		log.Fatal(err)
	}
}
