/* Zuordnung zu deinem Kursheft. Trage le (1–11) und seite ein, sobald das Inhaltsverzeichnis vorliegt. */
var HEFT_MAPPING = {
 "hinweis": "Zuordnung zum Kursheft „Handbuch zur Basisqualifizierung gemäß § 8 AnFöVO“ des Gemeindenahen Verbunds ATEMPAUSE (Kreis Siegen-Wittgenstein), nach dem Inhaltsverzeichnis (Heftseite 5) und den Heftseiten 7 und 44–52 (Fotos, selbst geprüft); Herausgeberangabe nach Kursplan und Heft S. 7, das Impressum des Hefts liegt nicht vor. Zugeordnet wurde nur, wenn der Seitentitel eindeutig zum Titel einer Lerneinheit passt; „seite“ ist der Seitenbereich der LE laut Inhaltsverzeichnis. le=null heißt offen.",
 "le": {
  "1": {
   "titel": "Einführung Angebote zur Unterstützung im Alltag",
   "seiten": "7–12"
  },
  "2": {
   "titel": "Grundlagenwissen Altersbilder",
   "seiten": "13–17"
  },
  "3": {
   "titel": "Basiswissen Krankheits- und Behinderungsbilder",
   "seiten": "18–30"
  },
  "4": {
   "titel": "Kommunikation und Gesprächsführung",
   "seiten": "31–43"
  },
  "5": {
   "titel": "Die Begleitung von Menschen mit Unterstützungsbedarf",
   "seiten": "44–52"
  },
  "6": {
   "titel": "An- und Zugehörige von Menschen mit Unterstützungsbedarf",
   "seiten": "53–61"
  },
  "7": {
   "titel": "Angebote für Menschen mit Unterstützungsbedarf und für ihre An- und Zugehörige",
   "seiten": "62–63"
  },
  "8": {
   "titel": "Die Sorge für mich selbst",
   "seiten": "64–73"
  },
  "9": {
   "titel": "Hauswirtschaft und Hygiene",
   "seiten": "74–77"
  },
  "10": {
   "titel": "Praktische Hilfen für die Begleitung von Menschen mit Unterstützungsbedarf",
   "seiten": "78–82"
  },
  "11": {
   "titel": "Rechtliche Rahmenbedingungen",
   "seiten": "83–90"
  }
 },
 "seiten": {
  "goal-E": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "e-was": {
   "le": 1,
   "seite": "7–12"
  },
  "e-pflegegrad": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "e-quali": {
   "le": 1,
   "seite": "7–12"
  },
  "cp-E": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M1": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m1-demenz": {
   "le": 3,
   "seite": "18–30"
  },
  "m1-delir": {
   "le": 3,
   "seite": "18–30"
  },
  "m1-krank": {
   "le": 3,
   "seite": "18–30"
  },
  "m1-ressourcen": {
   "le": 3,
   "seite": "18–30",
   "basis": "ABGELEITET (Kursheft 3.3.7, S. 27: ressourcen- und biografieorientiert)"
  },
  "le3-selbstbestimmung": {
   "le": 3,
   "seite": "18–30",
   "basis": "Kursheft 3.3.6, S. 26"
  },
  "le3-personenzentriert": {
   "le": 3,
   "seite": "18–30",
   "basis": "Kursheft 3.3.7, S. 26–28"
  },
  "le3-sessel": {
   "le": 3,
   "seite": "18–30",
   "basis": "Kursheft 3.3.7, S. 26–28"
  },
  "cp-M1": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M2": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m2-bewegen": {
   "le": 10,
   "seite": "78–82"
  },
  "m2-notruf": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m2-fast": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m2-herz-zucker": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m2-sturz": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m2-hygiene": {
   "le": 9,
   "seite": "74–77"
  },
  "le10-alltag": {
   "le": 10,
   "seite": "78–82"
  },
  "cp-M2": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M3": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m3-erst": {
   "le": null,
   "seite": null,
   "status": "offen",
   "hinweis": "bis v2.3.1 LE 5; laut Themenübersicht LE 5 (Kursheft S. 44) nicht enthalten, daher offen"
  },
  "m3-angeh": {
   "le": 6,
   "seite": "53–61"
  },
  "m3-sit": {
   "le": 6,
   "seite": "53–61"
  },
  "le5-kultur": {
   "le": 5,
   "seite": "44–52",
   "basis": "Kursheft 5.2, S. 46–48"
  },
  "le5-trauma": {
   "le": 5,
   "seite": "44–52",
   "basis": "Kursheft 5.3, S. 49–52"
  },
  "cp-M3": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M4": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m4-grund": {
   "le": 4,
   "seite": "31–43"
  },
  "m4-demenz": {
   "le": 4,
   "seite": "31–43"
  },
  "m4-verhalten": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m4-konflikt": {
   "le": 4,
   "seite": "31–43"
  },
  "le4-zuhoeren": {
   "le": 4,
   "seite": "31–43",
   "basis": "Kursheft S. 33 (Ende der Gesprächstechniken, Abschnittsnummer im Foto nicht genannt). Inhalt nach Transkription des Seitenfotos (gelesen am 09.11.2026); das Foto selbst lag auf der Box nicht vor."
  },
  "le4-gfk": {
   "le": 4,
   "seite": "31–43",
   "basis": "Kursheft 4.1.3, S. 33. Inhalt nach Transkription des Seitenfotos (gelesen am 09.11.2026); das Foto selbst lag auf der Box nicht vor."
  },
  "le4-beeintr": {
   "le": 4,
   "seite": "31–43",
   "basis": "Kursheft 4.4.2–4.4.5, Heftseite nicht belegt"
  },
  "cp-M4": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M5": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m5-pflichten": {
   "le": 11,
   "seite": "83–90"
  },
  "m5-grenze": {
   "le": 11,
   "seite": "83–90"
  },
  "m5-darf": {
   "le": 11,
   "seite": "83–90"
  },
  "m5-geld": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m5-netz": {
   "le": 7,
   "seite": "62–63"
  },
  "m5-vorsorge": {
   "le": 11,
   "seite": "83–90"
  },
  "m5-fem": {
   "le": 11,
   "seite": "83–90"
  },
  "le7-angebote": {
   "le": 7,
   "seite": "62–63"
  },
  "cp-M5": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M6": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m6-warum": {
   "le": 5,
   "seite": "44–52",
   "basis": "ABGELEITET (Kursheft 5.1.1, S. 44)"
  },
  "m6-beispiele": {
   "le": 5,
   "seite": "44–52",
   "basis": "ABGELEITET (Kursheft 5.1.1, S. 44–45)"
  },
  "m6-haushalt": {
   "le": 9,
   "seite": "74–77"
  },
  "le5-erinnerung": {
   "le": 5,
   "seite": "44–52",
   "basis": "Kursheft 5.1.1–5.1.2, S. 44–45"
  },
  "le5-paul": {
   "le": 5,
   "seite": "44–52",
   "basis": "Kursheft S. 45"
  },
  "cp-M6": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-M7": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m7-rolle": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "m7-abgrenzen": {
   "le": 8,
   "seite": "64–73"
  },
  "m7-selbst": {
   "le": 8,
   "seite": "64–73"
  },
  "m7-notizen": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "le2-altersbilder": {
   "le": 2,
   "seite": "13–17"
  },
  "le2-sprache": {
   "le": 2,
   "seite": "13–17",
   "basis": "Kursheft 2.3, S. 17. Inhalt nach Transkription des Seitenfotos (gelesen am 09.11.2026); das Foto selbst lag auf der Box nicht vor."
  },
  "cp-M7": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "goal-A": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "a-themen": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "a-trinken": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "a-zahlen": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "cp-A": {
   "le": null,
   "seite": null,
   "status": "offen"
  },
  "ende": {
   "le": null,
   "seite": null,
   "status": "offen"
  }
 }
};
var DATA = {"version": "2.10.0", "cardmods": ["E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "E", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M5", "M2", "M2", "M2", "M2", "M2", "M2", "M2", "A", "M4", "M4", "M4", "M7"], "glossary": {"Behandlungspflege": "Medizinische Pflege nach ärztlicher Verordnung, z. B. Medikamente, Injektionen, Verbände (häusliche Krankenpflege, § 37 SGB V).", "Entlastungsbetrag": "Bis zu 131 € im Monat, die die Pflegekasse für anerkannte Entlastungsangebote erstattet (§ 45b SGB XI; Stand 09.11.2026, für 2027 ist eine Änderung geplant, nur Entwurf).", "Pflegegrad": "Einstufung der Pflegebedürftigkeit von 1 bis 5 nach dem Grad der Selbstständigkeit (§ 15 SGB XI).", "Delir": "Plötzlich einsetzende, schwankende Verwirrtheit mit gestörtem Bewusstsein; ärztlich abzuklären.", "Demenz": "Erworbener, meist fortschreitender Abbau von Gedächtnis und Denkfähigkeiten, der den Alltag beeinträchtigt.", "Validation": "Haltung nach Naomi Feil: Gefühle und Erleben verwirrter Menschen gelten lassen statt zu korrigieren.", "Ressourcen": "Fähigkeiten, Vorlieben und Kontakte, die ein Mensch noch hat und nutzen kann.", "Vorsorgevollmacht": "Vollmacht, mit der jemand selbst bestimmt, wer für ihn handeln darf (§ 1820 BGB).", "Patientenverfügung": "Schriftliche Festlegung zu ärztlichen Maßnahmen für den Fall der Einwilligungsunfähigkeit (§ 1827 BGB).", "rechtliche Betreuung": "Vom Betreuungsgericht angeordnete Unterstützung für Volljährige, die Angelegenheiten nicht selbst rechtlich besorgen können (§ 1814 BGB).", "Freiheitsberaubung": "Einsperren oder anderweitiges Entziehen der Fortbewegungsfreiheit; strafbar nach § 239 StGB.", "Pflegeberatung": "Individuelle Beratung durch die Pflegekasse für Menschen mit Leistungen der Pflegeversicherung (§ 7a SGB XI).", "Selbstwirksamkeit": "Das Gefühl, durch eigenes Handeln etwas bewirken zu können.", "FAST": "Schnelltest bei Schlaganfallverdacht: Face, Arms, Speech, Time.", "Basisqualifizierung": "Pflichtschulung nach § 8 AnFöVO NRW mit mindestens 40 Unterrichtsstunden.", "NBA": "Neues Begutachtungsassessment: Verfahren mit sechs Modulen, mit dem die Pflegekasse den Pflegegrad ermittelt (§ 15 SGB XI).", "Medizinische Dienst": "Gutachterdienst, der im Auftrag der Pflegekasse die Pflegebedürftigkeit begutachtet (§ 18 SGB XI)."}, "modules": [["E", "Einführung: Alltagsbegleitung – was ist das?", "HB S. 1–3"], ["M1", "Modul 1 · Krankheit, Behinderung, Ressourcen", "HB S. 4–8"], ["M2", "Modul 2 · Unfälle vermeiden, Notfälle, Krisen", "HB S. 9–14"], ["M3", "Modul 3 · Unterstützungsbedarf, soziales Umfeld", "HB S. 15–17"], ["M4", "Modul 4 · Kommunikation und Konflikte", "HB S. 18–22"], ["M5", "Modul 5 · Recht und Versorgungssystem", "HB S. 23–28"], ["M6", "Modul 6 · Beschäftigung und Aktivierung", "HB S. 29–31"], ["M7", "Modul 7 · Rolle, Haltung, Grenzen", "HB S. 32–35"], ["A", "Anhang · Vertiefungsthemen", "Anhang S. 1–20"]], "quiz": {"E": [["Wie viele Unterrichtsstunden umfasst die Basisqualifizierung nach § 8 AnFöVO mindestens?", ["20", "30", "40", "160"], 2, "§ 8 Abs. 3 AnFöVO: mindestens 40 Unterrichtsstunden. 30 gelten nur bei rein hauswirtschaftlichem Angebot (Abs. 4)."], ["Bis wann soll die Qualifizierung abgeschlossen sein?", ["Vor dem ersten Einsatz", "Spätestens drei Monate nach Aufnahme der Tätigkeit", "Spätestens drei Monate nach der Anerkennung des Angebots", "Innerhalb eines Jahres"], 1, "§ 8 Abs. 1 Satz 3 AnFöVO: „spätestens drei Monate nach Aufnahme der Tätigkeit“. Eine Frist ab der Anerkennung nennt die Verordnung nicht."], ["Welches NBA-Modul (Begutachtung nach § 15 SGB XI) hat das größte Gewicht?", ["Mobilität", "Selbstversorgung", "Kognitive Fähigkeiten", "Alltagsleben"], 1, "Selbstversorgung zählt 40 % (§ 15 Abs. 2 SGB XI)."]], "M1": [["Was unterscheidet ein Delir typischerweise von einer Demenz?", ["Schleichender Beginn", "Plötzlicher Beginn und getrübtes Bewusstsein", "Es betrifft nur junge Menschen", "Es ist immer unheilbar"], 1, "Ein Delir beginnt plötzlich, das Bewusstsein ist gestört; es muss ärztlich abgeklärt werden."], ["Welche Demenzform ist am häufigsten?", ["Frontotemporale Demenz", "Lewy-Körperchen-Demenz", "Alzheimer-Krankheit", "Korsakow-Syndrom"], 2, "Alzheimer gilt übereinstimmend als häufigste Form (Fachstandard)."], ["Was bedeutet „ressourcenorientiert“?", ["Möglichst alles abnehmen", "Zuerst schauen, was die Person noch kann", "Kosten sparen", "Nur nach Plan arbeiten"], 1, "Vorhandene Fähigkeiten nutzen und erhalten (HB S. 7–8)."]], "M2": [["Wofür steht das T im FAST-Test?", ["Temperatur", "Time – sofort 112", "Tablette geben", "Trinken anbieten"], 1, "Time: Jede Minute zählt, sofort Notruf 112 (HB S. 5, 11)."], ["Eine wache Person zeigt Zeichen einer Unterzuckerung. Was tust du?", ["Insulin geben", "Traubenzucker oder Zuckerwasser geben und Hilfe rufen", "Nichts, abwarten", "Hinlegen und allein lassen"], 1, "HB S. 14: bei Bewusstsein Zucker anbieten, Rettungsdienst rufen."], ["Herr K. ist gestürzt und hat Schmerzen in der Hüfte. Was ist richtig?", ["Sofort hochziehen", "Liegen lassen, zudecken, 112 rufen, bei ihm bleiben", "Schmerztablette geben", "Später nachsehen"], 1, "Bei Bein- oder Hüftverletzung nicht aufstehen lassen (HB S. 14)."], ["Wie lange wirkt ein Händedesinfektionsmittel bei der hygienischen Händedesinfektion in der Regel ein?", ["5 Sekunden", "30 Sekunden", "3 Minuten", "10 Minuten"], 1, "So lange wie auf dem Mittel angegeben, meist 30 Sekunden (manche Mittel: 15 s; Fachstandard)."]], "M3": [["Was klärst du im Erstgespräch unbedingt?", ["Kontostand", "Notfallkontakte und was zu deiner Tätigkeit gehört", "Die Diagnose im Detail", "Nichts, erst einmal anfangen"], 1, "HB S. 15–16: Wünsche, Kontakte, Abgrenzung der Tätigkeit, nächster Termin."], ["Sind pflegende Angehörige Zielgruppe der Unterstützung?", ["Nein, nur die pflegebedürftige Person", "Ja, ihre Entlastung ist ausdrücklich Ziel", "Nur mit ärztlicher Verordnung", "Nur bei Pflegegrad 5"], 1, "HB S. 17; § 45b SGB XI nennt die Entlastung pflegender Angehöriger."], ["Wer hat Anspruch auf Pflegeberatung nach § 7a SGB XI?", ["Nur Pflegekräfte", "Personen, die Leistungen nach dem SGB XI erhalten oder beantragt haben", "Nur Privatversicherte", "Niemand"], 1, "§ 7a Abs. 1 SGB XI (bei Antrag: wenn erkennbar Beratungsbedarf besteht); auf Wunsch werden Angehörige einbezogen (Abs. 2)."]], "M4": [["Welche vier Seiten hat eine Nachricht nach Schulz von Thun?", ["Sach, Selbstoffenbarung, Beziehung, Appell", "Wer, wie, was, wann", "Laut, leise, schnell, langsam", "Frage, Antwort, Pause, Ende"], 0, "HB S. 18–19."], ["Wie sprichst du einen Menschen mit Demenz am besten an?", ["Von hinten, damit er nicht erschrickt", "Von vorne, mit Blickkontakt und kurzen Sätzen", "In Babysprache", "Möglichst schnell"], 1, "HB S. 21."], ["Eine Klientin beschuldigt dich, ihr Geld gestohlen zu haben. Was hilft?", ["Heftig widersprechen", "Gefühl ernst nehmen und gemeinsam suchen", "Polizei rufen", "Nicht mehr kommen"], 1, "Nicht rechtfertigen, gemeinsam suchen; Vorfall dem Anbieter melden (Fachstandard)."]], "M5": [["Wie hoch ist der Entlastungsbetrag 2026?", ["104 €", "125 €", "131 €", "150 €"], 2, "§ 45b Abs. 1 SGB XI: bis zu 131 € monatlich (bis 2024: 125 €)."], ["Ein Klient bittet dich, seine Tabletten für die Woche zu stellen. Was tust du?", ["Ich stelle sie sorgfältig", "Ich lehne ab und informiere Angehörige oder Pflegedienst", "Ich gebe sie direkt", "Ich frage die Nachbarin"], 1, "Medikamente richten ist Behandlungspflege (§ 37 SGB V), nicht Alltagsbegleitung."], ["Die Nachbarin fragt nach der Diagnose deiner Klientin. Was gilt?", ["Kurz erzählen ist ok", "Nur mit Zustimmung der Klientin weitergeben", "Erlaubt, wenn sie verwandt ist", "Erlaubt nach Dienstschluss"], 1, "Verschwiegenheit und Datenschutz (HB S. 24)."], ["Darfst du die Wohnungstür abschließen, damit eine Klientin mit Demenz nicht wegläuft?", ["Ja, zu ihrem Schutz", "Nein, eigenmächtiger Freiheitsentzug kann strafbar sein", "Ja, wenn sie schläft", "Ja, wenn die Nachbarn zustimmen"], 1, "§ 239 StGB; in Einrichtungen zusätzlich § 1831 Abs. 4 BGB."]], "M6": [["Was gilt, wenn jemand eine Beschäftigung ablehnt?", ["Weiter überreden", "Ablehnung akzeptieren", "Strafen", "Notieren und melden"], 1, "HB S. 31."], ["Woran passt du ein Aktivierungsangebot an?", ["An deinen Zeitplan", "An Fähigkeiten, Vorlieben und Tagesform", "An das Alter allein", "An den Pflegegrad allein"], 1, "HB S. 31."], ["Welche Tätigkeit eignet sich gut im Sitzen?", ["Fenster putzen", "Wäsche zusammenlegen oder Kartoffeln schälen", "Treppe wischen", "Rasen mähen"], 1, "HB S. 30."]], "M7": [["Ein Klient braucht Hilfe beim Duschen. Was folgt daraus?", ["Ich dusche ihn", "Das ist Pflege; ich hole weitere Hilfe dazu", "Ich lasse ihn allein", "Ich warte ab"], 1, "HB S. 34: Duschen und Verbandswechsel fallen in den Bereich der Pflege."], ["Was bedeutet emotionale Abgrenzung?", ["Gefühllos sein", "Mitfühlend sein, ohne fremde Gefühle zu übernehmen", "Kontakt vermeiden", "Nur noch telefonieren"], 1, "HB S. 35."], ["Welches Bedürfnis gehört zur Bedürfnisblume nach Kitwood?", ["Reichtum", "Identität", "Ruhm", "Kontrolle"], 1, "Liebe in der Mitte, darum Trost, Bindung, Einbeziehung, Beschäftigung, Identität (Kursheft S. 28; NRW-HB S. 34 nennt fünf, mit „Teilhabe“)."]], "A": [["Wie viel sollten Menschen ab 65 laut DGE etwa über Getränke aufnehmen, wenn ärztlich nichts anderes gilt?", ["0,5 l", "etwa 1,3 l", "3 l", "5 l"], 1, "DGE-Referenzwert für Getränke ab 65 Jahren: 1.310 ml/Tag (Fachstandard, nicht amtlich)."], ["Warum trinken ältere Menschen oft zu wenig?", ["Das Durstgefühl ist vermindert", "Wasser ist ungesund", "Aus Sparsamkeit", "Weil es verboten ist"], 0, "Vermindertes Durstgefühl; deshalb erinnern und anbieten."], ["Eine Person lehnt über längere Zeit Essen ab, ohne erkennbaren Grund. Was rätst du Angehörigen?", ["Nichts tun", "Pflegerischen oder ärztlichen Rat einholen", "Zwangsweise füttern", "Nahrungsergänzung kaufen"], 1, "Anhang S. 13."]]}, "cards": [["Mindestumfang der Basisqualifizierung?", "Mindestens 40 Unterrichtsstunden.", "§ 8 Abs. 3 AnFöVO"], ["Umfang bei rein hauswirtschaftlichem Angebot?", "Mindestens 30 Unterrichtsstunden, Inhalte Nr. 1–5.", "§ 8 Abs. 4 AnFöVO"], ["Wann soll die Qualifizierung abgeschlossen sein?", "Spätestens drei Monate nach Aufnahme der Tätigkeit.", "§ 8 Abs. 1 AnFöVO"], ["Wie viele Pflichtinhalte nennt § 8 Abs. 2?", "Sieben.", "§ 8 Abs. 2 AnFöVO"], ["Pflichtinhalt Nr. 2?", "Grundkenntnisse, um auf Notfälle und akute Krisen zu reagieren.", "§ 8 Abs. 2 Nr. 2 AnFöVO"], ["Pflichtinhalt Nr. 7?", "Kommunikations-, Handlungs- und Reflexionskompetenz, besonders bei herausforderndem Verhalten.", "§ 8 Abs. 2 Nr. 7 AnFöVO"], ["Wie lange muss Pflegebedürftigkeit voraussichtlich bestehen?", "Mindestens sechs Monate.", "§ 14 Abs. 1 SGB XI"], ["Wie viele Pflegegrade gibt es?", "Fünf.", "§ 15 SGB XI"], ["Gewicht des NBA-Moduls Selbstversorgung (§ 15 SGB XI)?", "40 Prozent.", "§ 15 Abs. 2 SGB XI"], ["Gewicht des NBA-Moduls Mobilität (§ 15 SGB XI)?", "10 Prozent.", "§ 15 Abs. 2 SGB XI"], ["Wie zählen NBA-Modul 2 und 3 (§ 15 SGB XI)?", "Zusammen 15 Prozent; der höhere Wert zählt.", "§ 15 Abs. 2 SGB XI"], ["Ab wie vielen Punkten Pflegegrad 1?", "Ab 12,5 Gesamtpunkten.", "§ 15 Abs. 3 SGB XI"], ["Ab wie vielen Punkten Pflegegrad 5?", "Ab 90 Gesamtpunkten (oder besondere Bedarfskonstellation).", "§ 15 Abs. 3, 4 SGB XI"], ["Wer begutachtet bei gesetzlich Versicherten?", "Der Medizinische Dienst oder beauftragte unabhängige Gutachter.", "§ 18 SGB XI"], ["Höhe des Entlastungsbetrags?", "Bis zu 131 Euro monatlich.", "§ 45b Abs. 1 SGB XI"], ["Wer hat Anspruch auf den Entlastungsbetrag?", "Pflegebedürftige in häuslicher Pflege, Pflegegrade 1–5.", "§ 45b SGB XI"], ["Bis wann sind Restbeträge nutzbar?", "Im folgenden Kalenderhalbjahr, also bis 30. Juni des Folgejahres.", "§ 45b Abs. 1 SGB XI"], ["Umwandlungsanspruch: ab welchem Pflegegrad, wie viel?", "Ab PG 2, bis zu 40 % des Sachleistungsbetrags.", "§ 45a Abs. 4 SGB XI"], ["Wo ist häusliche Krankenpflege geregelt?", "§ 37 SGB V.", "§ 37 SGB V"], ["Darfst du Medikamente richten oder geben?", "Nein. Das ist Behandlungspflege; Angehörige, Pflegedienst oder Arztpraxis informieren.", "HB S. 25; § 37 SGB V"], ["Darfst du beim Duschen helfen?", "Nein, das ist körperbezogene Pflege.", "HB S. 34"], ["Ist Gartenarbeit eine Leistung der Alltagsbegleitung?", "Nein; Begleiten bei der Gartenarbeit ist erlaubt.", "HB S. 25"], ["An wen gibst du Privates über Klient:innen weiter?", "Nur mit deren Zustimmung.", "HB S. 24"], ["Gelten mündliche Absprachen als Vertrag?", "Ja.", "HB S. 23"], ["Was ist eine Patientenverfügung?", "Schriftliche Festlegung zu ärztlichen Maßnahmen für den Fall der Einwilligungsunfähigkeit.", "§ 1827 BGB"], ["Wann ist eine rechtliche Betreuung nicht erforderlich?", "Wenn z. B. eine bevollmächtigte Person die Angelegenheiten ebenso gut besorgen kann.", "§ 1814 Abs. 3 BGB"], ["Welche Strafnorm droht bei eigenmächtigem Einschließen?", "Freiheitsberaubung, § 239 StGB.", "§ 239 StGB"], ["Wann braucht eine FEM die Genehmigung des Betreuungsgerichts?", "Wenn ein Betreuer sie in Krankenhaus, Heim oder Einrichtung länger oder regelmäßig veranlasst.", "§ 1831 Abs. 4 BGB"], ["Welche Norm regelt unterlassene Hilfeleistung?", "§ 323c StGB.", "§ 323c StGB"], ["Notrufnummer für Rettungsdienst?", "112.", "—"], ["Was bedeutet FAST?", "Face, Arms, Speech, Time.", "HB S. 5"], ["Was gibst du bei Schlaganfallverdacht nicht?", "Keine Getränke, keine Medikamente (Schluckstörung möglich).", "HB S. 12"], ["Erste Hilfe bei Unterzuckerung, Person wach?", "Traubenzucker oder Zuckerwasser, Rettungsdienst rufen.", "HB S. 14"], ["Sturz mit Hüftschmerz: aufstehen lassen?", "Nein. Liegen lassen, zudecken, 112, dabeibleiben.", "HB S. 14"], ["Einwirkzeit hygienische Händedesinfektion?", "So lange wie auf dem Mittel angegeben, meist 30 Sekunden (manche Mittel: 15 s).", "KRINKO; Aktion Saubere Hände 2020; infektionsschutz.de 2025"], ["Trinkmenge im Alter (Richtwert)?", "Etwa 1,3 Liter Getränke pro Tag ab 65 (DGE: 1.310 ml; Fachstandard).", "DGE"], ["Vier Seiten einer Nachricht?", "Sachinhalt, Selbstoffenbarung, Beziehungshinweis, Appell.", "HB S. 18–19"], ["Wie sprichst du Menschen mit Demenz an?", "Von vorne, ruhig, kurze Sätze, keine Babysprache.", "HB S. 21"], ["Wer entwickelte die Validation?", "Naomi Feil.", "Fachstandard"], ["Bedürfnisblume nach Kitwood: Was steht in der Mitte, was drumherum?", "In der Mitte Liebe; drumherum Trost, Bindung, Einbeziehung, Beschäftigung, Identität.", "Kursheft S. 28; NRW-HB S. 34"]]};
(function(){
'use strict';
var PREFIX='anfoevo_v2_', VERSION=DATA.version;
// ---------- Speicher mit Fallback ----------
var Store={ok:false,mem:{},
 init:function(){try{var k=PREFIX+'__t';window.localStorage.setItem(k,'1');window.localStorage.removeItem(k);this.ok=true;}catch(e){this.ok=false;}return this.ok;},
 get:function(k,d){var v=null;if(this.ok){try{v=window.localStorage.getItem(PREFIX+k);}catch(e){v=null;}}else{v=Object.prototype.hasOwnProperty.call(this.mem,k)?this.mem[k]:null;}
  if(v===null||v===undefined)return d;try{return JSON.parse(v);}catch(e){return d;}},
 set:function(k,val){var s=JSON.stringify(val);if(this.ok){try{window.localStorage.setItem(PREFIX+k,s);return;}catch(e){this.ok=false;showStoreNote();}}this.mem[k]=s;}
};
var S={};
function loadState(){S.gaps=Store.get('gaps',{});S.darf=Store.get('darf',{});S.exam=Store.get('exam',null);S.done=Store.get('done',{});S.cards=Store.get('cards',{});S.quiz=Store.get('quiz',{});S.notes=Store.get('notes',{});S.prefs=Store.get('prefs',{});S.endtest=Store.get('endtest',{});}
function save(k){Store.set(k,S[k]);}
function showStoreNote(){var n=document.getElementById('storenote');if(n)n.hidden=false;}


// ---------- Suche (Nachschlagen) ----------
// Normalisierung wie normAns: ä→ae, ö→oe, ü→ue, ß→ss, Akzente weg; dazu Variante ae→a, oe→o, ue→u (beidseitig)
function norm(s){return String(s||'').toLowerCase().replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue').replace(/ß/g,'ss').normalize('NFD').replace(/[\u0300-\u036f]/g,'');}
function variant(n){return n.replace(/ae/g,'a').replace(/oe/g,'o').replace(/ue/g,'u');}
function buildIndex(){pages.forEach(function(a){var t=norm(a.textContent+' '+(a.dataset.k||''));a._t=t;a._v=variant(t);});}
function termHit(a,w){return a._t.indexOf(w.n)>=0||a._v.indexOf(w.v)>=0;}
function parseTerms(q){return norm(q).split(/\s+/).filter(Boolean).map(function(n){return {n:n,v:variant(n)};});}
var lastQ='',setNavH=function(){};
function applySearch(q){
 q=q||'';lastQ=q;var terms=parseTerms(q), any=0;
 if(!pages.length||pages[0]._t===undefined)buildIndex();
 pages.forEach(function(a){var hit=terms.every(function(w){return termHit(a,w);});a.classList.toggle('hidden',!hit);if(hit)any++;});
 $$('.unit').forEach(function(u){var m=u.dataset.mod;var vis=$$('article.page[data-mod="'+m+'"]').some(function(a){return !a.classList.contains('hidden');});u.classList.toggle('hidden',!vis);});
 $('#nores').hidden=any>0;  var hc=$('#hits');if(hc)hc.textContent=terms.length?(any===1?'1 Seite gefunden':any+' Seiten gefunden'):'';
 var sc=$('#sclear');if(sc)sc.hidden=!q;
 highlight(terms);setNavH();
 return any;}
// Treffer markieren: Normalisierung zeichengenau zurückrechnen
function normMap(s){var out='',map=[];for(var i=0;i<s.length;i++){var c=norm(s.charAt(i));for(var j=0;j<c.length;j++){out+=c.charAt(j);map.push(i);}}return {n:out,map:map};}
function varMap(m){var out='',map=[],n=m.n;for(var i=0;i<n.length;i++){var c=n.charAt(i);if(c==='e'&&i>0&&/[aou]/.test(n.charAt(i-1)))continue;out+=c;map.push(m.map[i]);}return {n:out,map:map};}
function findRanges(s,terms){var r=[],m=normMap(s),v=varMap(m);
 terms.forEach(function(w){[[m,w.n],[v,w.v]].forEach(function(p){var src=p[0],t=p[1],k=0;if(!t)return;while((k=src.n.indexOf(t,k))>=0){var st=src.map[k],en=src.map[k+t.length-1]+1;r.push([st,en]);k+=t.length;}});});
 r.sort(function(a,b){return a[0]-b[0];});var o=[];r.forEach(function(x){var l=o[o.length-1];if(l&&x[0]<=l[1])l[1]=Math.max(l[1],x[1]);else o.push(x.slice());});return o;}
function clearMarks(){$$('mark.hit').forEach(function(mk){var p=mk.parentNode;p.replaceChild(document.createTextNode(mk.textContent),mk);p.normalize();});}
function highlight(terms){clearMarks();terms=terms.filter(function(w){return w.n.length>=2;});if(!terms.length)return 0;var cnt=0;
 pages.forEach(function(a){if(a.classList.contains('hidden'))return;
  $$('p,li,h3,td,summary',a).forEach(function(el){
   var tw=document.createTreeWalker(el,4,null),nodes=[],nd;while((nd=tw.nextNode()))nodes.push(nd);
   nodes.forEach(function(tn){var par=tn.parentNode;if(!par||(par.closest&&par.closest('.gap,.gph,button,mark,textarea,.marker,.loesung,a,label')))return;
    var s=tn.nodeValue;if(!s||!s.trim())return;var rg=findRanges(s,terms);if(!rg.length)return;
    var frag=document.createDocumentFragment(),pos=0;rg.forEach(function(x){if(x[0]>pos)frag.appendChild(document.createTextNode(s.slice(pos,x[0])));var mk=document.createElement('mark');mk.className='hit';mk.textContent=s.slice(x[0],x[1]);frag.appendChild(mk);cnt++;pos=x[1];});
    if(pos<s.length)frag.appendChild(document.createTextNode(s.slice(pos)));par.replaceChild(frag,tn);});});});
 return cnt;}


// ---------- Prüfungsfragen (Karten) ----------
var ci=0;
function cardPool(){var f=$('#cardfilter').value;var r=[];for(var i=0;i<DATA.cards.length;i++){var v=S.cards[i];if(f==='all'||(f==='open'&&v!=='known')||(f==='weak'&&(v==='unsure'||v==='unknown')))r.push(i);}return r;}
function sureCount(mod){var n=0,k=0;for(var i=0;i<DATA.cards.length;i++){if(!mod||DATA.cardmods[i]===mod){n++;if(S.cards[i]==='known')k++;}}return [k,n];}
function showCard(){var o=cardPool(),c=$('#card');var t=sureCount();
 $('#cardstat').textContent=t[0]+' von '+t[1]+' sicher';
 $('#ca').hidden=true;$('#cs').hidden=true;$('#rateRow').hidden=true;$('#reveal').hidden=false;
 if(!o.length){c.dataset.i='';$('#cq').textContent=$('#cardfilter').value==='weak'?'Keine Schwachstellen markiert.':'Alle Fragen sicher. Stark!';$('#reveal').hidden=true;renderSure();updateReadBar();return;}
 if(o.indexOf(ci)<0)ci=o[0];var cd=DATA.cards[ci];c.dataset.i=ci;
 $('#cq').textContent='Frage '+(ci+1)+': '+cd[0];$('#ca').textContent=cd[1];$('#cs').textContent='Quelle: '+cd[2]+' · geprüft am 09.11.2026';renderSure();updateReadBar();}
function flip(){$('#ca').hidden=false;$('#cs').hidden=false;$('#rateRow').hidden=false;$('#reveal').hidden=true;}
function rate(v){if($('#card').dataset.i===''||$('#ca').hidden)return false;S.cards[ci]=v;save('cards');var o=cardPool();var nx=null;for(var k=0;k<o.length;k++){if(o[k]>ci){nx=o[k];break;}}ci=nx!==null?nx:(o.length?o[0]:0);showCard();updateProgress();return true;}
function renderSure(){var h='<tr><th>Modul</th><th>sicher</th></tr>';DATA.modules.forEach(function(m){var c=sureCount(m[0]);if(c[1])h+='<tr><td>'+esc(m[1])+'</td><td>'+c[0]+' von '+c[1]+'</td></tr>';});$('#suretab').innerHTML=h;}

// ---------- Selbstcheck ----------
var examQ=[];
function allQ(){var r=[];Object.keys(DATA.quiz).forEach(function(m){DATA.quiz[m].forEach(function(q,i){r.push([m,i]);});});return r;}
function startExam(n){var a=allQ();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;}examQ=a.slice(0,Math.min(n,a.length));
 $('#exambox').innerHTML=examQ.map(function(x,k){var q=DATA.quiz[x[0]][x[1]];return '<fieldset data-k="'+k+'"><legend>'+(k+1)+'. '+esc(q[0])+'</legend>'+q[1].map(function(o,oi){return '<label class="opt exam-opt"><input type="radio" name="ex'+k+'" value="'+oi+'"> '+esc(o)+'</label>';}).join('')+'<p class="expl" hidden></p></fieldset>';}).join('');
 $('#exameval').hidden=false;$('#examres').textContent='';return examQ.length;}
function evalExam(){var per={},tot=0;examQ.forEach(function(x,k){var q=DATA.quiz[x[0]][x[1]];var fs=$('#exambox fieldset[data-k="'+k+'"]');var sel=$('input:checked',fs);var v=sel?+sel.value:-1;var ok=v===q[2];
  $$('input',fs).forEach(function(inp){inp.disabled=true;});$$('.exam-opt',fs).forEach(function(l,oi){if(oi===q[2])l.classList.add('ok');if(oi===v&&!ok)l.classList.add('bad');});
  var ex=$('.expl',fs);ex.hidden=false;ex.textContent=(ok?'✓ Richtig. ':(v<0?'✗ Nicht beantwortet. ':'✗ Nicht ganz. '))+q[3];
  per[x[0]]=per[x[0]]||[0,0];per[x[0]][1]++;if(ok){per[x[0]][0]++;tot++;}});
 var h='<p><b>'+tot+' von '+examQ.length+' richtig ('+Math.round(100*tot/examQ.length)+' %)</b></p><table class="suretab"><tr><th>Modul</th><th>richtig</th></tr>';
 DATA.modules.forEach(function(m){if(per[m[0]])h+='<tr><td>'+esc(m[1])+'</td><td>'+(per[m[0]][0]===per[m[0]][1]?'✓ ':'✗ ')+per[m[0]][0]+' von '+per[m[0]][1]+'</td></tr>';});
 $('#examres').innerHTML=h+'</table><p class="quizscore">Orientierung, kein amtlicher Bewertungsmaßstab. Schwache Module gezielt wiederholen.</p>';$('#exameval').hidden=true;
 S.exam={date:new Date().toISOString(),score:tot,total:examQ.length,per:per};save('exam');return {score:tot,total:examQ.length,per:per};}

// ---------- Kopieren ----------
function copyText(t,btn){function ok(){if(btn){var o=btn.textContent;btn.textContent='Kopiert ✓';setTimeout(function(){btn.textContent=o;},1500);}}
 if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(t).then(ok,fallback);}else fallback();
 function fallback(){var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();try{document.execCommand('copy');ok();}catch(e){alert('Bitte manuell kopieren.');}ta.remove();}}

var $=function(s,r){return (r||document).querySelector(s);}, $$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s));};
var pages=[], list=[], idx=0, mode='blaettern';
var VIEWS=['inhalt','blaettern','suche','geschafft','karten','exam','foto','fortschritt','quellen','info'];
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}

// ---------- Fortschritt ----------
function taskFields(a){return $$('.task .gap-in, .task textarea',a);}
function allFilled(a){var f=taskFields(a);return f.length>0&&f.every(function(x){return x.value.trim()!=='';});}
function isDone(a){var t=a.dataset.type;
 if(t==='checkpoint'){var q=S.quiz[a.dataset.mod]||{};var n=+a.dataset.nq;for(var i=0;i<n;i++){if(q[i]===undefined)return false;}return true;}
 if(a.dataset.id==='ende'){return $$('fieldset.et',a).every(function(fs){return S.endtest[fs.dataset.k]!==undefined;});}
 if(a.dataset.id==='m5-darf'){return $$('fieldset.darf').every(function(fs){return S.darf[fs.dataset.i]!==undefined;});}
 return !!S.done[a.dataset.id]||allFilled(a);}
function exercisesOf(mod){return $$('article.page[data-mod="'+mod+'"]').filter(function(a){return a.dataset.fill==='1';});}
function ensureProgressRings(){if(!document.querySelector('.ring')){$$('.prog').forEach(function(p){var w=p.querySelector('.ring-wrap');if(w)return;var wrap=document.createElement('span');wrap.className='ring-wrap';var svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('class','ring');svg.setAttribute('viewBox','0 0 40 40');svg.setAttribute('aria-hidden','true');var bg=document.createElementNS('http://www.w3.org/2000/svg','circle');bg.setAttribute('class','ring-bg');bg.setAttribute('cx','20');bg.setAttribute('cy','20');bg.setAttribute('r','16');var fg=document.createElementNS('http://www.w3.org/2000/svg','circle');fg.setAttribute('class','ring-fg');fg.setAttribute('cx','20');fg.setAttribute('cy','20');fg.setAttribute('r','16');fg.setAttribute('stroke-dasharray','100.5');fg.setAttribute('stroke-dashoffset','100.5');svg.appendChild(bg);svg.appendChild(fg);wrap.appendChild(svg);var pct=document.createElement('span');pct.className='ring-pct';pct.textContent='0%';wrap.appendChild(pct);var bar=p.querySelector('.bar');if(bar)bar.parentNode.insertBefore(wrap,bar);});}}
function updateProgress(){
 ensureProgressRings();
 var allExercises=$$('article.page[data-fill="1"]');var totalDone=allExercises.filter(isDone).length,totalEx=allExercises.length;
 DATA.modules.forEach(function(m){var ex=exercisesOf(m[0]);var d=ex.filter(isDone).length;
  $$('.prog[data-mod="'+m[0]+'"]').forEach(function(p){var pct=ex.length?Math.round(100*d/ex.length):0;p.querySelector('i').style.width=pct+'%';var fg=p.querySelector('.ring-fg');if(fg)fg.setAttribute('stroke-dashoffset',String(100.5*(1-pct/100)));var rp=p.querySelector('.ring-pct');if(rp)rp.textContent=pct+'%';var sc=sureCount(m[0]);p.querySelector('.prog-count').textContent=d+' von '+ex.length+' Aufgaben erledigt'+(sc[1]?' · '+sc[0]+' von '+sc[1]+' Prüfungsfragen sicher':'');});});
 updateToc();
 var md=$('#markdone'),cur=list[idx];if(md&&cur){md.setAttribute('aria-pressed',S.done[cur.dataset.id]?'true':'false');}
 updateReadBar();
 // Overall ring
 var op=document.getElementById('prog-overall-pct'),ot=document.getElementById('prog-overall-txt'),ofg=document.querySelector('#prog-overall .ring-fg');
 var overallPct=totalEx?Math.round(100*totalDone/totalEx):0;
 if(op)op.textContent=overallPct+' %';
 if(ot)ot.textContent=totalDone+' von '+totalEx+' Aufgaben erledigt';
 if(ofg)ofg.setAttribute('stroke-dashoffset',String(150.8*(1-overallPct/100)));}
// ---------- Inhaltsverzeichnis (je LE: x von y ausgefüllt) ----------
function updateToc(){var groups={};
 $$('#toc a.tocl').forEach(function(l){var a=document.getElementById('p-'+l.dataset.goto);if(!a)return;var g=l.closest('.tocle').dataset.g;groups[g]=groups[g]||[0,0];
  l.classList.toggle('cur',!!(list[idx]&&list[idx]===a));if(l.classList.contains('tocread'))return;var d=isDone(a);groups[g][1]++;if(d)groups[g][0]++;
  l.classList.toggle('done',d);var st=l.querySelector('.tocst');if(st)st.textContent=d?'✓':'○';var sr=l.querySelector('.tocsr');if(sr)sr.textContent=d?' (ausgefüllt)':' (offen)';});
 $$('#toc .tocle').forEach(function(sec){var c=groups[sec.dataset.g]||[0,0];var p=sec.querySelector('.tocprog');if(p)p.textContent=c[0]+' von '+c[1]+' ausgefüllt';var i=sec.querySelector('.bar>i');if(i)i.style.width=(c[1]?100*c[0]/c[1]:0)+'%';sec.classList.toggle('alldone',c[1]>0&&c[0]===c[1]);});
 var r=$('#resume');if(r){var any=pages.some(function(a){return a.dataset.fill==='1'&&isDone(a);});var cur=list[idx];r.textContent=(any&&cur)?'Weiter bei: '+cur.dataset.title:'Los geht’s: erste Seite';}}
function updateReadBar(){var f=0;
 if(mode==='blaettern'){f=list.length?(idx+1)/list.length:0;}
 else if(mode==='karten'){var sc=sureCount();f=sc[0]/sc[1];}
 else{var h=document.documentElement.scrollHeight-window.innerHeight;f=h>0?window.scrollY/h:0;}
 $('#readprog>div').style.width=Math.max(0,Math.min(1,f))*100+'%';}

// ---------- Blättern ----------
function leNum(a){var n=+a.dataset.le;return n>0?n:99;}
var tempAll=false; // nur für einen gezielten Sprung (Link/Suche) auf eine Seite ohne Ausfüllteil; wird nicht gespeichert
function onlyFillOn(){return S.prefs.onlyfill!==false&&!tempAll;}
function syncAllBox(){var c=$('#allpages');if(c)c.checked=!onlyFillOn();}
function leSort(arr){return arr.slice().sort(function(x,y){return leNum(x)-leNum(y)||(+x.dataset.order)-(+y.dataset.order);});}
function setPrintOrder(){leSort(pages.filter(function(a){return a.dataset.fill==='1';})).forEach(function(a,i){a.style.order=String(i);});pages.forEach(function(a){if(a.dataset.fill!=='1')a.style.order='999';});}
function buildList(){var onlyFill=onlyFillOn();return pages.filter(function(a){return !onlyFill||a.dataset.fill==='1';}).slice().sort(function(x,y){return leNum(x)-leNum(y)||(+x.dataset.order)-(+y.dataset.order);});}
function leInfo(a,mod){var n=+a.dataset.le,L=window.HEFT_MAPPING&&HEFT_MAPPING.le&&HEFT_MAPPING.le[n];return L?('Kursheft LE '+n+' · '+L.titel+' (S. '+L.seiten+')'):(mod?('Ergänzung · '+mod[1]):('Abschluss · '+a.dataset.title));}
var flipDir=0;
// ---------- v2.5: Schrittanzeige, „LE geschafft“ ----------
function leKey(a){return a.dataset.le||(a.dataset.id==='ende'?'ende':'z');}
function leName(k){if(k==='ende')return 'Abschluss';if(k==='z')return 'Ergänzungen';var L=HEFT_MAPPING.le[k];return 'LE '+k+(L?': '+L.titel:'');}
function stepInfo(a){var k=leKey(a);var same=list.filter(function(x){return leKey(x)===k;});var i=same.indexOf(a)+1;return (k==='ende'?'Abschluss':k==='z'?'Ergänzung':'LE '+k)+' · Seite '+i+' von '+same.length;}
function weiter(){var a=list[idx],b=list[idx+1];if(!a||!b)return;if(leKey(a)!==leKey(b)){showDone(a,b);return;}next();}
function showDone(a,b){var k=leKey(a),same=list.filter(function(x){return leKey(x)===k;}),d=same.filter(isDone).length;
 $('#done-h').textContent=(k==='z'?'Ergänzungen':k==='ende'?'Abschluss':'LE '+k)+' geschafft';
 $('#done-p').textContent='Du hast '+d+' von '+same.length+' Seiten ausgefüllt.'+(d<same.length?' Offene Seiten findest du im Inhalt (○).':' Super!');
 var nk=leKey(b);$('#done-next').textContent=nk==='ende'?'Weiter zum Abschluss':nk==='z'?'Weiter mit den Ergänzungen':'Weiter mit '+leName(nk);
 setMode('geschafft');try{window.scrollTo(0,0);}catch(e){}var h=$('#done-h');h.setAttribute('tabindex','-1');try{h.focus({preventScroll:true});}catch(e){}}
// ---------- v2.5: Hintergrund aus Video-Einzelbildern (Bildsequenz auf <canvas>) ----------
var BG={frames:{},cur:null,anim:0,played:0,off:false,ctx:null,pending:0,preloadPromise:null,playing:0};
function bgName(s,i){return s+(i<10?'0':'')+i;}
function bgSeq(s){var r=[];for(var i=0;i<14;i++)r.push(bgName(s,i));return r;}
function mq(q){try{return window.matchMedia&&matchMedia(q).matches;}catch(e){return false;}}
function bgInit(){var cv=$('#bgc');var c2=null;try{c2=cv&&cv.getContext&&cv.getContext('2d');}catch(e){}
 var sd=navigator.connection&&navigator.connection.saveData;
 if(!c2||mq('(prefers-reduced-data: reduce)')||sd){BG.off=true;document.documentElement.classList.add('bg-off');return;}
 BG.cv=cv;BG.ctx=c2;BG.dir=(Math.min(screen.width||innerWidth,innerWidth)<=700?'m':'d');BG.base=document.body.getAttribute('data-bg')||'bg/';
 bgSize();window.addEventListener('resize',function(){if(BG.rz)return;BG.rz=requestAnimationFrame(function(){BG.rz=0;bgSize();if(BG.cur)bgDraw(BG.cur);});},{passive:true});
 bgLoad('r00').then(function(ok){if(ok&&bgDraw('r00'))document.documentElement.classList.add('bg-on');});
 var idle=window.requestIdleCallback||function(f){return setTimeout(f,400);};
 var later=function(){idle(function(){if(!mq('(prefers-reduced-motion: reduce)'))bgPreloadAll();});};
 if(document.readyState==='complete')later();else window.addEventListener('load',later);}
function bgLoad(n){if(BG.frames[n])return BG.frames[n].p;var im=new Image();im.decoding='async';var f={im:im,ready:false};
 f.p=new Promise(function(res){im.onload=function(){var d=im.decode?im.decode():Promise.resolve();d.then(function(){f.ready=true;res(true);},function(){f.ready=true;res(true);});};im.onerror=function(){res(false);};});
 BG.frames[n]=f;im.src=BG.base+BG.dir+'/'+n+'.webp';return f.p;}
function bgPreloadAll(){
 if(BG.preloadPromise)return BG.preloadPromise;
 var names=['r00'].concat(bgSeq('w'),bgSeq('z'));
 var prog=document.getElementById('bgprog'),bar=prog?prog.querySelector('div'):null,lbl=prog?prog.querySelector('.bgprog-label'):null;
  if(prog){prog.hidden=false;requestAnimationFrame(function(){prog.classList.add('show');});}
  var done=0;function tick(){done++;if(bar)bar.style.width=Math.round(done/names.length*100)+'%';if(lbl)lbl.textContent='Hintergrund wird geladen… '+done+'/'+names.length;}
  BG.preloadPromise=Promise.all(names.map(function(n){return bgLoad(n).then(function(r){tick();return r;});})).then(function(results){BG.preloadPromise=null;if(prog){setTimeout(function(){prog.classList.remove('show');setTimeout(function(){prog.hidden=true;if(bar)bar.style.width='0%';},300);},400);}return results.every(Boolean);},function(){BG.preloadPromise=null;if(prog){prog.classList.remove('show');prog.hidden=true;}return false;});
 return BG.preloadPromise;
}
function bgSize(){var d=Math.min(window.devicePixelRatio||1,1.5);BG.cv.width=Math.max(1,Math.round(innerWidth*d));BG.cv.height=Math.max(1,Math.round(innerHeight*d));}
function bgDraw(n){var f=BG.frames[n];if(!f||!f.ready||!BG.ctx)return false;var im=f.im,cw=BG.cv.width,ch=BG.cv.height,sc=Math.max(cw/im.naturalWidth,ch/im.naturalHeight),w=im.naturalWidth*sc,h=im.naturalHeight*sc;BG.ctx.drawImage(im,(cw-w)/2,(ch-h)/2,w,h);BG.cur=n;return true;}
function bgTurn(dir){
 if(BG.off||!BG.ctx||mq('(prefers-reduced-motion: reduce)')){BG.pending=0;return false;}
 var seq=bgSeq(dir>0?'w':'z');
 if(!seq.every(function(n){return BG.frames[n]&&BG.frames[n].ready;})){
  cancelAnimationFrame(BG.anim);BG.anim=0;BG.playing=0;BG.pending=dir>0?1:-1;
  bgPreloadAll().then(function(ok){var pending=BG.pending;BG.pending=0;if(!pending)return;if(ok)bgTurn(pending);else{bgDraw('r00');}});
  return false;
 }
 BG.pending=0;cancelAnimationFrame(BG.anim);BG.anim=0;var t0=0,FD=42;BG.playing=dir;
 function step(t){if(!t0)t0=t;var k=Math.floor((t-t0)/FD);if(k>=seq.length){BG.anim=0;bgDraw('r00');BG.playing=0;BG.played++;return;}bgDraw(seq[k]);BG.anim=requestAnimationFrame(step);}
 BG.anim=requestAnimationFrame(step);return true;
}
function render(){
 var old=document.querySelector('article.page.current');
 pages.forEach(function(a){a.classList.remove('current','flip');});
 if(!list.length){$('#pagerinfo').textContent='–';return;}
 idx=Math.max(0,Math.min(idx,list.length-1));
 var a=list[idx];a.classList.add('current');var turning=!!(flipDir&&a!==old);if(turning){document.body.classList.add('page-turning');window.clearTimeout(window.__bookTurnTimer);window.__bookTurnTimer=window.setTimeout(function(){document.body.classList.remove('page-turning');},820);a.style.setProperty('--dir',flipDir>0?'18px':'-18px');a.style.setProperty('--turn',flipDir>0?'1.2deg':'-1.2deg');void a.offsetWidth;a.classList.add('flip');}var stage=document.getElementById('object-stage');if(stage){var progress=list.length?(idx/(list.length-1||1)):0;stage.style.setProperty('--book-fill',String(Math.max(.035,1-progress)));stage.setAttribute('aria-hidden','true');}flipDir=0;
 var mod=DATA.modules.filter(function(m){return m[0]===a.dataset.mod;})[0];
 $('#curmod').textContent=leInfo(a,mod);var si=stepInfo(a);$('#curstep').textContent=si;
 syncAllSol(a);$('#weiter2').disabled=idx===list.length-1;$('#zurueck2').disabled=idx===0;
 $('#pagerinfo').innerHTML='<span class="vhid">Lernseite </span>'+(idx+1)+'/'+list.length;$('#tocbtn').setAttribute('aria-label','Inhalt öffnen · Lernseite '+(idx+1)+' von '+list.length);
 if(mode==='blaettern'&&history.replaceState){try{history.replaceState(null,'','#p='+encodeURIComponent(a.dataset.id));}catch(e){}}
 $('#prev').disabled=idx===0;$('#next').disabled=idx===list.length-1;
 S.prefs.pos=a.dataset.id;save('prefs');updateProgress();window.dispatchEvent(new Event('kompendium:pagechange'));}
function goTo(i){idx=i;render();if(mode==='blaettern'){try{window.scrollTo(0,0);}catch(e){}}}
function next(){if(mode==='inhalt'){setMode('blaettern');return;}if(idx<list.length-1){flipDir=1;bgTurn(1);goTo(idx+1);}}
function prev(){if(mode==='inhalt'){setMode('blaettern');return;}if(idx>0){flipDir=-1;bgTurn(-1);goTo(idx-1);}}
function findIn(id){for(var i=0;i<list.length;i++){if(list[i].dataset.id===id)return i;}return -1;}
function rebuild(keepId,force){list=buildList();var j=keepId?findIn(keepId):-1;
 if(j<0&&force&&keepId&&document.getElementById('p-'+keepId)){tempAll=true;syncAllBox();list=buildList();j=findIn(keepId);}
 idx=j>=0?j:0;render();}
function handleSwipe(dx,dy){if(mode!=='blaettern')return false;if(Math.abs(dx)<50||Math.abs(dx)<Math.abs(dy))return false;if(dx<0)next();else prev();return true;}

// ---------- Ansichten ----------
function setMode(m){if(VIEWS.indexOf(m)<0)m='blaettern';mode=m;
 var b=document.body;b.classList.remove('mode-suche','mode-blaettern','mode-other','mode-inhalt');
 var view=(m==='suche'||m==='blaettern')?'heft':m;
 b.classList.add(view==='heft'||m==='inhalt'?'mode-'+m:'mode-other');
 var tb=$('#tocbtn');if(tb)tb.setAttribute('aria-expanded',m==='inhalt'?'true':'false');
 $$('.view').forEach(function(v){v.classList.toggle('active',v.id==='view-'+view);});
 closeMenu();
 if(m==='blaettern'){applySearch('');rebuild(S.prefs.pos,forceNext);}
 if(m==='inhalt'){applySearch('');if(!list.length)list=buildList();if(!$('article.page.current')){var j=findIn(S.prefs.pos);idx=j>=0?j:0;}render();}
 if(m==='suche'){applySearch($('#search').value);}
 if(m==='karten'){showCard();}
 if(m==='fortschritt'){updateProgress();}
 if(m!=='suche'&&m!=='geschafft'){S.prefs.mode=m;save('prefs');}
 updateReadBar();setNavH();}
function openMenu(){$('#mehrmenu').hidden=false;$('#mehr').setAttribute('aria-expanded','true');}
function closeMenu(){var mm=$('#mehrmenu');if(mm){mm.hidden=true;$('#mehr').setAttribute('aria-expanded','false');}}
function toggleMenu(){if($('#mehrmenu').hidden)openMenu();else closeMenu();}

// ---------- Lückentexte ----------
function normAns(s){return String(s||'').toLowerCase().replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue').replace(/ß/g,'ss').replace(/[€%§]/g,function(c){return {'€':'euro','%':'prozent','§':''}[c];}).replace(/[.]/g,',').replace(/[^a-z0-9,]/g,'');}
function gapAlts(g){try{return JSON.parse(g.dataset.alts);}catch(e){return [];}}
function checkGap(g,val){var alts=gapAlts(g),v=normAns(val),fb=$('.gap-fb',g);g.classList.remove('ok','bad');
 if(!v){fb.textContent='○ leer';return false;}
 var ok=alts.some(function(a){return normAns(a)===v;});g.classList.add(ok?'ok':'bad');haptic(ok?8:15);
 fb.textContent=ok?'✓ passt':'✗ vergleiche mit Lösung ('+(g.dataset.key.split('-').pop())+')';return ok;}
function setGap(g,val){var i=$('.gap-in',g);i.value=val;i.classList.toggle('filled',!!val.trim());S.gaps[g.dataset.key]=val;if(!val)delete S.gaps[g.dataset.key];save('gaps');}
// ---------- Ankreuzen (Checkpoint, Darf ich das?) ----------
function answer(mod,qi,oi){var fs=$('fieldset[data-mod="'+mod+'"][data-q="'+qi+'"]');var r=$$('input[type=radio]',fs)[oi];r.checked=true;S.quiz[mod]=S.quiz[mod]||{};S.quiz[mod][qi]=oi;save('quiz');evalTaskIfOpen(fs);updateProgress();var _ok=oi===DATA.quiz[mod][qi][2];setMood(_ok);haptic(_ok?8:15);return _ok;}
function darfAnswer(i,v){var fs=$('fieldset.darf[data-i="'+i+'"]');$$('input[type=radio]',fs).forEach(function(r){r.checked=r.value===v;});S.darf[i]=v;save('darf');evalTaskIfOpen(fs);updateProgress();var _ok=v===fs.dataset.a;setMood(_ok);haptic(_ok?8:15);return _ok;}
function showEt(fs){var v=S.endtest[fs.dataset.k],fb=$('.etfb',fs),right=+fs.dataset.right;$$('label.ropt',fs).forEach(function(l){l.classList.remove('ok','bad');});if(v===undefined){fb.textContent='';fb.className='etfb';return null;}
 var ok=+v===right,labs=$$('label.ropt',fs);labs[right].classList.add('ok');if(!ok&&labs[+v])labs[+v].classList.add('bad');
 fb.className='etfb '+(ok?'ok':'bad');fb.textContent=(ok?'✓ Richtig. ':'✗ Leider falsch. Richtig ist: „'+labs[right].textContent.trim()+'“. ')+fs.dataset.expl;return ok;}
function etScore(){var a=$('#p-ende');if(!a)return;var fs=$$('fieldset.et',a),n=0,c=0;fs.forEach(function(f){var v=S.endtest[f.dataset.k];if(v!==undefined){n++;if(+v===+f.dataset.right)c++;}});$('.etscore',a).textContent=n?(c+' von '+fs.length+' richtig'+(n<fs.length?' ('+(fs.length-n)+' offen)':'')):'';}
function endAnswer(k,v){var fs=$('fieldset.et[data-k="'+k+'"]');$$('input[type=radio]',fs).forEach(function(r){r.checked=+r.value===+v;});S.endtest[k]=+v;save('endtest');var ok=showEt(fs);etScore();updateProgress();setMood(ok);haptic(ok?8:15);if(ok){var _fs=$$('fieldset.et',$('#p-ende'));var _n=0,_c=0;_fs.forEach(function(f){var v=S.endtest[f.dataset.k];if(v!==undefined){_n++;if(+v===+f.dataset.right)_c++;}});if(_n===_fs.length&&_c===_n&&_fs.length>0){confettiBurst();haptic([30,50,30]);}}return ok;}
function markRadios(fs,right){$$('label.ropt',fs).forEach(function(l){var r=$('input',l);l.classList.remove('ok','bad');if(r.value===String(right))l.classList.add('ok');else if(r.checked)l.classList.add('bad');});}
function evalTask(task){var c=0,n=0;
 $$('.gap',task).forEach(function(g){n++;if(checkGap(g,$('.gap-in',g).value))c++;});
 $$('fieldset[data-mod]',task).forEach(function(fs){n++;var it=DATA.quiz[fs.dataset.mod][+fs.dataset.q];markRadios(fs,it[2]);var ch=$('input:checked',fs);if(ch&&+ch.value===it[2])c++;});
 $$('fieldset.darf',task).forEach(function(fs){n++;markRadios(fs,fs.dataset.a);var ch=$('input:checked',fs);if(ch&&ch.value===fs.dataset.a)c++;});
 var sc=$('.quizscore',task);if(sc)sc.textContent=n?(c+' von '+n+' richtig'):'';return [c,n];}
function clearEval(task){$$('.gap',task).forEach(function(g){g.classList.remove('ok','bad');$('.gap-fb',g).textContent='';});$$('label.ropt',task).forEach(function(l){l.classList.remove('ok','bad');});var sc=$('.quizscore',task);if(sc)sc.textContent='';}
function updateGapMood(task,editedGap){var gaps=$$('.gap',task),allFilled=gaps.length>0,hasWrong=false;gaps.forEach(function(g){var input=$('.gap-in',g),value=input?input.value:'';if(!normAns(value)){allFilled=false;return;}if(!gapAlts(g).some(function(a){return normAns(a)===normAns(value);}))hasWrong=true;});if(hasWrong){setMood(false);return;}if(allFilled){setMood(true);return;}if(editedGap)setMood(checkGap(editedGap,$('.gap-in',editedGap).value));}
function evalTaskIfOpen(el){var t=el.closest('.task');if(!t)return;var d=$('details.loesung',t);if(d&&d.open){evalTask(t);if(el.classList.contains('gap-in'))updateGapMood(t,el.closest('.gap'));}}
// v2.5 (Alex t46u): „Alle Lösungen dieser Seite zeigen“ (schnell zum Abschreiben); kein exklusives Akkordeon
function syncAllSol(a){var b=$('#allsol');if(!b)return;a=a||$('article.page.current');var L=a?$$('details.loesung,details.schluessel',a):[];b.hidden=!L.length;var all=L.length&&L.every(function(d){return d.open;});b.setAttribute('aria-pressed',all?'true':'false');b.textContent=all?'Lösungen dieser Seite zuklappen':'Alle Lösungen dieser Seite zeigen';}
function toggleAllSol(){var a=$('article.page.current');if(!a)return 0;var L=$$('details.loesung,details.schluessel',a);var open=!L.every(function(d){return d.open;});L.forEach(function(d){d.open=open;if(!d.classList.contains('loesung'))return;var t=d.closest('.task');if(open){evalTask(t);updateGapMood(t,null);}else clearEval(t);});syncAllSol(a);return L.length;}
function openSolution(a,open){var d=$('details.loesung',a);if(!d)return null;d.open=open!==false;var t=d.closest('.task');if(d.open){var result=evalTask(t);updateGapMood(t,null);return result;}clearEval(t);return null;}

// ---------- Wiederherstellen / Löschen ----------
function restoreAll(){
 $$('.gap').forEach(function(g){var v=S.gaps[g.dataset.key]||'';var i=$('.gap-in',g);i.value=v;i.classList.toggle('filled',!!v.trim());});
 $$('textarea.notes').forEach(function(t){t.value=S.notes[t.dataset.id]||'';t.classList.toggle('filled',!!t.value.trim());});
 $$('fieldset[data-mod]').forEach(function(fs){var q=(S.quiz[fs.dataset.mod]||{})[fs.dataset.q];$$('input[type=radio]',fs).forEach(function(r){r.checked=q!==undefined&&+r.value===q;});});
 $$('fieldset.darf').forEach(function(fs){var v=S.darf[fs.dataset.i];$$('input[type=radio]',fs).forEach(function(r){r.checked=v!==undefined&&r.value===v;});});
 $$('fieldset.et').forEach(function(fs){var v=S.endtest[fs.dataset.k];$$('input[type=radio]',fs).forEach(function(r){r.checked=v!==undefined&&+r.value===+v;});showEt(fs);});etScore();
 $$('details.loesung').forEach(function(d){d.open=false;clearEval(d.closest('.task'));});
 syncPrintVals();updateProgress();}
function doClearAll(){['gaps','done','cards','quiz','notes','darf','endtest'].forEach(function(k){S[k]={};save(k);});S.exam=null;save('exam');restoreAll();showCard();}
function clearAll(ask){if(ask===false){doClearAll();return true;}if(window.confirm!==nativeConfirm){if(!window.confirm('Alle Eingaben und den Fortschritt auf diesem Gerät löschen? Das lässt sich nicht rückgängig machen.'))return false;doClearAll();return true;}uiConfirm('Alle Eingaben und den Fortschritt auf diesem Gerät löschen? Das lässt sich nicht rückgängig machen.',function(ok){if(!ok)return;doClearAll();updateProgress();});return false;}

// ---------- Export / Import ----------
function exportData(){return {app:'anfoevo_v2',version:VERSION,exported:new Date().toISOString(),data:{gaps:S.gaps,done:S.done,cards:S.cards,quiz:S.quiz,notes:S.notes,darf:S.darf,exam:S.exam,endtest:S.endtest,prefs:S.prefs}};}
function importData(obj){
 if(!obj||obj.app!=='anfoevo_v2'||!obj.data||typeof obj.data!=='object'||Array.isArray(obj.data))throw new Error('Keine gültige Fortschrittsdatei dieses Kompendiums.');
 var keys=['gaps','done','cards','quiz','notes','darf','exam','endtest','prefs'],next={},present=[];
 keys.forEach(function(k){
  if(!Object.prototype.hasOwnProperty.call(obj.data,k))return;
  var v=obj.data[k];
  if(k==='exam'&&v===null){next[k]=null;present.push(k);return;}
  if(!v||typeof v!=='object'||Array.isArray(v))throw new Error('Ungültiges Datenfeld: '+k);
  next[k]=v;present.push(k);
 });
 if(!present.length)throw new Error('Die Fortschrittsdatei enthält keine unterstützten Datenfelder.');
 var previous={};present.forEach(function(k){previous[k]=S[k];});
 try{present.forEach(function(k){S[k]=next[k];save(k);});restoreAll();showCard();if(present.indexOf('prefs')>=0){applyTheme(themeOf());updateThemeColor();}}
 catch(e){present.forEach(function(k){S[k]=previous[k];save(k);});try{restoreAll();}catch(ignore){}throw e;}
 return true;
}
function download(){uiConfirm('Sicherung jetzt speichern? Die Datei landet im Download-Ordner.',function(ok){if(!ok)return;var ts=new Date().toISOString().slice(0,10);var blob=new Blob([JSON.stringify(exportData(),null,2)],{type:'application/json'});var a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='anfoevo_v2_fortschritt_'+ts+'.json';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},500);var f=$('#savedflash');if(f){f.textContent='Sicherungsdownload gestartet.';clearTimeout(flashT);flashT=setTimeout(function(){f.textContent='';},2500);}});}
function upload(file){if(!file)return;if(file.size>5*1024*1024){alert('Import abgebrochen: Die Datei ist größer als 5 MB.');return;}var r=new FileReader();r.onerror=function(){alert('Import fehlgeschlagen: Datei konnte nicht gelesen werden.');};r.onload=function(){try{importData(JSON.parse(r.result));alert('Fortschritt importiert.');}catch(e){alert('Import fehlgeschlagen: '+e.message);}};r.readAsText(file);}

// ---------- Druck ----------
var printing=false;
function prePrint(){if(printing)return;printing=true;setPrintOrder();var sol=document.documentElement.classList.contains('print-sol');$$('details').forEach(function(d){d.dataset.wasOpen=d.open?'1':'';d.open=sol||!(d.classList.contains('loesung')||d.classList.contains('schluessel'));});
 $$('.gap-in,textarea.notes').forEach(function(i){i.classList.toggle('filled',!!i.value.trim());});
 syncPrintVals();}
function syncPrintVals(t0){(t0?[t0]:$$('textarea.notes')).forEach(function(t){var p=t.nextElementSibling;if(!p||!p.classList.contains('printval')){p=document.createElement('div');p.className='printval';p.setAttribute('aria-hidden','true');t.parentNode.insertBefore(p,t.nextSibling);}p.textContent=t.value;});}
function postPrint(){if(!printing)return;printing=false;$$('details').forEach(function(d){d.open=d.dataset.wasOpen==='1';});document.documentElement.classList.remove('print-sol');}
// v2.5: zweite Druckart „Mit Lösungen drucken“ (Standard bleibt: leere Ausfüllseiten)
function printWithSolutions(){closeMenu();document.documentElement.classList.add('print-sol');prePrint();try{window.print();}catch(e){}}
// Fallback für Browser ohne beforeprint/afterprint: matchMedia('print')
function watchPrintMedia(){try{var mq=window.matchMedia('print');var f=function(e){if(e.matches)prePrint();else postPrint();};if(mq.addEventListener)mq.addEventListener('change',f);else if(mq.addListener)mq.addListener(f);}catch(e){}}

// ---------- Init ----------
function focusSearch(){if(mode!=='suche'&&mode!=='blaettern')setMode('blaettern');var s=$('#search');s.focus();try{s.select();}catch(e){}return s;}
function onSearchInput(){var v=$('#search').value;if(v.trim()){if(mode!=='suche')setMode('suche');else applySearch(v);}else{if(mode==='suche')setMode('blaettern');else applySearch('');}}
function onScroll(){document.body.classList.toggle('scrolled',(window.scrollY||0)>80);if(mode!=='blaettern'&&mode!=='karten')updateReadBar();}
function goToId(id){var s=$('#search');if(s.value){s.value='';}S.prefs.pos=id;forceNext=true;if(mode!=='blaettern')setMode('blaettern');else{applySearch('');rebuild(id,true);}forceNext=false;var a=list[idx];return a&&a.dataset.id===id;}
var forceNext=false;
var flashT=null;function flashSaved(){var f=$('#savedflash');if(!f)return;f.textContent=Store.ok?'💾 gespeichert':'⚠ nur bis zum Schließen gespeichert';clearTimeout(flashT);flashT=setTimeout(function(){f.textContent='';},1600);}
function loadSelfTest(){var src=document.getElementById('selftest-src');if(window.__selftestLoaded||!src)return;window.__selftestLoaded=true;var sc=document.createElement('script');sc.textContent=src.textContent;document.body.appendChild(sc);}
window.runSelfTest=function(){loadSelfTest();if(window.runSelfTest.__stub)throw new Error('Selbsttest konnte nicht geladen werden');return window.runSelfTest();};window.runSelfTest.__stub=true;
/* ---------- Darstellung: Automatik / Hell / Dunkel (v2.10.0, Phase 1) ----------
   Vorwahl in S.prefs.theme ('auto'|'hell'|'dunkel'); 'auto' folgt dem System.
   applyTheme setzt data-theme am Wurzelelement – style.css legt dafür eigene Token ab. */
var THEME_ORDER=['auto','hell','dunkel'],THEME_LABEL={auto:'Automatik',hell:'Hell',dunkel:'Dunkel'};
function themeOf(){var t=S.prefs&&S.prefs.theme;return THEME_ORDER.indexOf(t)>=0?t:'auto';}
function systemDark(){return !!(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches);}
function applyTheme(t){var r=document.documentElement;if(!t||t==='auto')r.removeAttribute('data-theme');else r.setAttribute('data-theme',t);var b=document.getElementById('themebtn');if(b)b.textContent='🌗 Darstellung: '+THEME_LABEL[t||'auto'];}
function updateThemeColor(){var t=themeOf(),m=document.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',(t==='dunkel'||(t==='auto'&&systemDark()))?'#14181d':'#294b3d');}
function cycleTheme(){var t=themeOf(),n=THEME_ORDER[(THEME_ORDER.indexOf(t)+1)%THEME_ORDER.length];if(S.prefs){S.prefs.theme=n;save('prefs');}applyTheme(n);updateThemeColor();}
window.cycleTheme=cycleTheme;window.applyTheme=function(t){applyTheme(t||themeOf());updateThemeColor();};
function init(){
 Store.init();loadState();if(!Store.ok){showStoreNote();$('#savestate').textContent='⚠ Nicht dauerhaft gespeichert (nur bis zum Schließen)';}
 applyTheme(themeOf());updateThemeColor();
 if(navigator.storage&&navigator.storage.persist){try{navigator.storage.persist().catch(function(){});}catch(e){}}
 pages=$$('article.page');pages.forEach(function(a,i){a.dataset.order=i;});
 var idle=window.requestIdleCallback||function(f){return setTimeout(f,200);};idle(function(){if(pages.length&&pages[0]._t===undefined)buildIndex();});
 var indexedAtBoot=pages.length>0&&pages[0]._t!==undefined;
 setPrintOrder();
 var hdr=$('#top');setNavH=function(){document.documentElement.style.setProperty('--navh',hdr.offsetHeight+'px');};
 setNavH();if(window.ResizeObserver){new ResizeObserver(function(){setNavH();}).observe(hdr);}else{window.addEventListener('resize',setNavH);}
 $('#search').addEventListener('input',onSearchInput);
 $('#sclear').addEventListener('click',function(){var s=$('#search');s.value='';onSearchInput();s.focus();});
 $('#allpages').addEventListener('change',function(e){tempAll=false;S.prefs.onlyfill=!e.target.checked;save('prefs');syncAllBox();rebuild(list[idx]&&list[idx].dataset.id);});
 $('#prev').addEventListener('click',prev);$('#next').addEventListener('click',next);
 $('#printbtn').addEventListener('click',function(){window.print();});
 $('#printsol').addEventListener('click',printWithSolutions);
 $('#backheft').addEventListener('click',function(){setMode('blaettern');});
 $('#tocbtn').addEventListener('click',function(){setMode(mode==='inhalt'?'blaettern':'inhalt');try{window.scrollTo(0,0);}catch(e){}});
 $('#weiter2').addEventListener('click',function(){weiter();});$('#zurueck2').addEventListener('click',function(){prev();});
 $('#done-next').addEventListener('click',function(){setMode('blaettern');next();});$('#done-toc').addEventListener('click',function(){setMode('inhalt');try{window.scrollTo(0,0);}catch(e){}});
 $('#view-quellen').addEventListener('click',function(e){var l=e.target.closest('a.qgo');if(!l)return;e.preventDefault();goToId(l.getAttribute('href').slice(3));try{window.scrollTo(0,0);}catch(x){}});
 $('#resume').addEventListener('click',function(){setMode('blaettern');try{window.scrollTo(0,0);}catch(e){}});
 $('#toc').addEventListener('click',function(e){var l=e.target.closest('a.tocl');if(!l)return;e.preventDefault();goToId(l.dataset.goto);try{window.scrollTo(0,0);}catch(x){}var h=$('#p-'+l.dataset.goto+' h3');if(h){h.setAttribute('tabindex','-1');try{h.focus({preventScroll:true});}catch(x){}}});
 $('#mehr').addEventListener('click',function(e){e.stopPropagation();toggleMenu();});
 $$('#mehrmenu .mi[data-go]').forEach(function(b){b.addEventListener('click',function(){setMode(b.dataset.go);try{window.scrollTo(0,0);}catch(e){}});});
 $('#markdone').addEventListener('click',function(){var a=list[idx];if(!a)return;if(mode!=='blaettern')setMode('blaettern');var id=a.dataset.id;var completed=!S.done[id];if(completed)S.done[id]=true;else delete S.done[id];save('done');updateProgress();if(completed){setMood(true);confettiBurst();haptic([20,40,20]);}});
 document.addEventListener('click',function(e){var mm=$('#mehrmenu');if(!mm.hidden&&!e.target.closest('#mehrmenu,#mehr'))closeMenu();});
 $('#pages').addEventListener('input',function(e){var t=e.target;
  if(t.classList.contains('gap-in')){setGap(t.closest('.gap'),t.value);evalTaskIfOpen(t);updateProgress();flashSaved();}
  else if(t.matches('textarea.notes')){S.notes[t.dataset.id]=t.value;if(!t.value)delete S.notes[t.dataset.id];save('notes');t.classList.toggle('filled',!!t.value.trim());syncPrintVals(t);updateProgress();flashSaved();}});
 $('#pages').addEventListener('change',function(e){var t=e.target;if(t.type!=='radio')return;var fs=t.closest('fieldset');
  if(fs.classList.contains('et'))endAnswer(fs.dataset.k,+t.value);else if(fs.classList.contains('darf'))darfAnswer(+fs.dataset.i,t.value);else if(fs.dataset.mod)answer(fs.dataset.mod,+fs.dataset.q,+t.value);flashSaved();});
 $$('details.loesung').forEach(function(d){d.addEventListener('toggle',function(){var t=d.closest('.task');if(d.open){evalTask(t);updateGapMood(t,null);}else clearEval(t);var a=d.closest('article.page');if(a&&a.classList.contains('current'))syncAllSol(a);});});
 $('#allsol').addEventListener('click',toggleAllSol);
 document.addEventListener('keydown',function(e){
  var confirmDialog=$('#confirmDlg');if(confirmDialog&&confirmDialog.open)return;
  if(e.key==='Enter'&&e.target.classList&&e.target.classList.contains('gap-in')){e.preventDefault();var all=$$('.gap-in').filter(function(x){return x.getClientRects().length;});var k=all.indexOf(e.target);if(all[k+1])all[k+1].focus();return;}
  if(e.key==='Escape'){if(!$('#mehrmenu').hidden){closeMenu();$('#mehr').focus();return;}if(e.target.id==='search'){e.target.value='';onSearchInput();return;}}
  if((e.ctrlKey||e.metaKey)&&!e.altKey&&(e.key==='k'||e.key==='K')){e.preventDefault();focusSearch();return;}
  if(e.target.closest&&e.target.closest('input,textarea,select,[contenteditable]'))return;
  if(e.key==='/'&&!e.ctrlKey&&!e.metaKey&&!e.altKey){e.preventDefault();focusSearch();return;}
  if(mode==='blaettern'){if(e.key==='ArrowRight')next();if(e.key==='ArrowLeft')prev();}});
 var sx=0,sy=0,root=$('#pages');
 root.addEventListener('touchstart',function(e){var t=e.changedTouches&&e.changedTouches[0];if(t){sx=t.clientX;sy=t.clientY;}},{passive:true});
 root.addEventListener('touchend',function(e){var t=e.changedTouches&&e.changedTouches[0];if(t)handleSwipe(t.clientX-sx,t.clientY-sy);},{passive:true});
 $('#reveal').addEventListener('click',flip);['known','unsure','unknown'].forEach(function(v){$('#r-'+v).addEventListener('click',function(){rate(v);});});
 $('#cardfilter').addEventListener('change',showCard);
 $('#examstart').addEventListener('click',function(){startExam(+$('#examn').value);});$('#exameval').addEventListener('click',evalExam);
 $('#cardsreset').addEventListener('click',function(){uiConfirm('Kartenfortschritt zurücksetzen?',function(ok){if(ok){S.cards={};save('cards');ci=0;showCard();}});});
 $('#clearall').addEventListener('click',function(e){e.preventDefault();clearAll();});
 $('#exportlink').addEventListener('click',function(e){e.preventDefault();download();});
 $$('.importfile').forEach(function(inp){inp.addEventListener('change',function(){if(inp.files[0])upload(inp.files[0]);inp.value='';});});
 $('#copyprompt').addEventListener('click',function(e){copyText($('#prompttext').textContent,e.target);});
 $('#runtest').addEventListener('click',function(){window.runSelfTest();});
 var _themebtn=$('#themebtn');if(_themebtn)_themebtn.addEventListener('click',cycleTheme);
 API.boot={prefsHadOnlyfill:Object.prototype.hasOwnProperty.call(S.prefs,'onlyfill'),indexedAtBoot:indexedAtBoot};
 window.addEventListener('scroll',onScroll,{passive:true});
 window.addEventListener('beforeprint',prePrint);window.addEventListener('afterprint',postPrint);watchPrintMedia();
 window.addEventListener('hashchange',function(){var h=location.hash;if(/^#p=/.test(h)){goToId(decodeURIComponent(h.slice(3)));}});
 restoreAll();syncAllBox();bgInit();
 var m=S.prefs.mode||'inhalt';var h=location.hash;
 if(/^#p=/.test(h)){S.prefs.pos=decodeURIComponent(h.slice(3));m='blaettern';forceNext=true;}
 if(VIEWS.indexOf(m)<0||m==='suche')m='blaettern';
 list=buildList();setMode(m);forceNext=false;
 API.boot.listLen=list.length;API.boot.allFill=list.every(function(a){return a.dataset.fill==='1';});API.boot.boxChecked=$('#allpages').checked;API.boot.pagerinfo=$('#pagerinfo').textContent;
 if(h==='#selftest'||/[?&]test(=|&|$)/.test(location.search)){window.__AUTOTEST=true;setMode('info');window.runSelfTest();}
}
/* v2.10.0 (V7): window.KOMP wird genau EINMAL gesetzt. Das Objekt entsteht vor init();
   init() hängt nur boot an dieselbe Instanz. 53 Mitglieder + boot = 54 (docs/api-snapshot.txt). */
var API={toggleAllSol:toggleAllSol,Store:Store,S:S,applySearch:applySearch,setMode:setMode,goTo:goTo,goToId:goToId,next:next,prev:prev,rebuild:rebuild,list:function(){return list;},idx:function(){return idx;},
 answer:answer,darfAnswer:darfAnswer,endAnswer:endAnswer,openSolution:openSolution,evalTask:evalTask,setGap:setGap,checkGap:checkGap,normAns:normAns,isDone:isDone,clearAll:clearAll,restoreAll:restoreAll,prePrint:prePrint,postPrint:postPrint,
 showCard:showCard,flip:flip,rate:rate,exportData:exportData,importData:importData,handleSwipe:handleSwipe,startExam:startExam,evalExam:evalExam,sureCount:sureCount,updateProgress:updateProgress,
 focusSearch:focusSearch,flashSaved:flashSaved,setPrintOrder:setPrintOrder,onlyFillOn:onlyFillOn,syncAllBox:syncAllBox,setTempAll:function(v){tempAll=!!v;syncAllBox();},onScroll:onScroll,bg:function(){return BG;},bgTurn:bgTurn,weiter:weiter,stepInfo:stepInfo,norm:norm,findRanges:findRanges,highlight:highlight,openMenu:openMenu,closeMenu:closeMenu,state:function(){return S;},mode:function(){return mode;}};
window.KOMP=API;
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
/* PWA: register only on http(s). file:// and android_asset stay usable without a worker. */
(function () {
  if (!('serviceWorker' in navigator)) return;
  var proto = location.protocol;
  if (proto !== 'http:' && proto !== 'https:') return;
  if (/android_asset/i.test(location.href) || /appassets\.androidplatform\.net/i.test(location.href)) return;
  window.__pwaRegisterAttempted = true;
  function register() {
    navigator.serviceWorker.register('./sw.js').then(function (reg) {
      if (!reg) return;
      reg.addEventListener('updatefound', function () {
        var nw = reg.installing;
        if (nw) nw.addEventListener('statechange', function () {
          if (nw.state === 'installed' && navigator.serviceWorker.controller) {
            window.dispatchEvent(new Event('pwa:update-ready'));
          }
        });
      });
    }).catch(function () {});
  }
  if (document.readyState === 'complete') register();
  else window.addEventListener('load', register);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'visible' && navigator.serviceWorker.controller) {
      navigator.serviceWorker.getRegistration().then(function (r) {
        if (r) r.update().catch(function () {});
      }).catch(function () {});
    }
  });
})();
function setMood(ok){var rb=document.querySelector('.robot3d');if(!rb)return;rb.classList.remove('mood-ok','mood-bad');rb.classList.add(ok?'mood-ok':'mood-bad');clearTimeout(rb._m);rb._m=setTimeout(function(){rb.classList.remove('mood-ok','mood-bad');},1600);}function confettiBurst(){if(window.matchMedia&&window.matchMedia('(prefers-reduced-motion:reduce)').matches)return;var c=document.createElement('canvas'),ctx=null;try{ctx=c.getContext('2d');}catch(e){return;}if(!ctx)return;c.style.cssText='position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:9999';document.body.appendChild(c);var W=c.width=window.innerWidth,H=c.height=window.innerHeight;var parts=[];for(var i=0;i<120;i++)parts.push({x:W/2,y:H/3,vx:(Math.random()-.5)*12,vy:Math.random()*-12-4,g:.35,r:Math.random()*4+2,a:1,col:'hsl('+(Math.random()*360|0)+',80%,60%)'});var t=0;(function loop(){t++;ctx.clearRect(0,0,W,H);var alive=false;parts.forEach(function(p){p.vy+=p.g;p.x+=p.vx;p.y+=p.vy;p.vx*=.99;p.a-=.012;if(p.a>0&&p.y<H+20){alive=true;ctx.globalAlpha=Math.max(0,p.a);ctx.fillStyle=p.col;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();}});ctx.globalAlpha=1;if(alive&&t<120)requestAnimationFrame(loop);else c.remove();})();}var m=document.querySelector('meta[name="theme-color"]');if(m){var d=matchMedia('(prefers-color-scheme:dark)');function up(){if(window.applyTheme)window.applyTheme();else m.setAttribute('content',d.matches?'#14181d':'#294b3d');}up();d.addEventListener?d.addEventListener('change',up):d.addListener(up);}window.confettiBurst=confettiBurst;window.setMood=setMood;var nativeConfirm=window.confirm;function uiConfirm(msg,done){if(window.confirm!==nativeConfirm){done(window.confirm(msg));return;}var dlg=document.getElementById('confirmDlg');if(!dlg||typeof dlg.showModal!=='function'){done(window.confirm(msg));return;}dlg.querySelector('.dlg-msg').textContent=msg;var ok=dlg.querySelector('.dlg-ok'),cancel=dlg.querySelector('.dlg-cancel');function cleanup(){ok.removeEventListener('click',onOk);cancel.removeEventListener('click',onCancel);dlg.removeEventListener('cancel',onCancelDlg);try{dlg.close();}catch(e){}}function onOk(){cleanup();done(true);}function onCancel(){cleanup();done(false);}function onCancelDlg(){cleanup();done(false);}ok.addEventListener('click',onOk);cancel.addEventListener('click',onCancel);dlg.addEventListener('cancel',onCancelDlg);dlg.showModal();}window.uiConfirm=uiConfirm;window.addEventListener('kompendium:pagechange',function(){setMood(true);});
// ---------- Parallax-Stage (nur Desktop) ----------
(function(){if(!window.matchMedia||!matchMedia('(hover:hover) and (pointer:fine)').matches)return;if(window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches)return;var st=document.getElementById('object-stage');if(!st)return;var tx=0,ty=0,raf=0;function flush(){raf=0;st.style.setProperty('--par-x',(tx*3).toFixed(3)+'deg');st.style.setProperty('--par-y',(-ty*2).toFixed(3)+'deg');}document.addEventListener('mousemove',function(e){var dx=(e.clientX/(innerWidth||1))-.5,dy=(e.clientY/(innerHeight||1))-.5;tx=dx;ty=dy;if(!raf)raf=requestAnimationFrame(flush);},{passive:true});})();
// ---------- Haptic Feedback (Android) ----------
function haptic(ms){if(navigator.vibrate)try{navigator.vibrate(ms||12);}catch(e){}}
window.haptic=haptic;
// ---------- Präsentationsmodus ----------
function togglePraesentation(on){
  var body=document.body, nav=document.getElementById('praesNav'), exit=document.getElementById('praesExit');
  if(on){body.classList.add('praesentation');if(nav)nav.hidden=false;if(exit)exit.hidden=false;updatePraesInfo();}
  else{body.classList.remove('praesentation');if(nav)nav.hidden=true;if(exit)exit.hidden=true;}
}
function updatePraesInfo(){var info=document.getElementById('praesInfo');if(!info)return;var K=window.KOMP;if(!K)return;var L=K.list(),i=K.idx();var cur=L&&L[i];var t=cur?cur.dataset.title||'Seite '+(i+1):'Seite '+(i+1);info.textContent=t+' ('+(i+1)+'/'+(L?L.length:0)+')';}
var _praesKeyHandler=null,_praesAutoStop=null;
function startPraesentation(){togglePraesentation(true);var K=window.KOMP;if(K)K.setMode('blaettern');
  var prevBtn=document.getElementById('praesPrev'),nextBtn=document.getElementById('praesNext'),exitBtn=document.getElementById('praesExit');
  if(prevBtn)prevBtn.onclick=function(){if(K)K.prev();updatePraesInfo();};
  if(nextBtn)nextBtn.onclick=function(){if(K)K.next();updatePraesInfo();};
  if(exitBtn)exitBtn.onclick=function(){stopPraesentation();};
  /* Auto-Play: stop fest verdrahtet, damit stopPraesentation ihn erreicht */
  var autoBtn=document.getElementById('praesAuto');var autoTimer=null;var autoOn=false;
  _praesAutoStop=function(){autoOn=false;if(autoTimer){clearInterval(autoTimer);autoTimer=null;}if(autoBtn)autoBtn.textContent='▶ Auto';};
  function startAuto(){autoOn=true;if(autoBtn)autoBtn.textContent='⏸ Stopp';autoTimer=setInterval(function(){var L=K?K.list():0,i=K?K.idx():0;if(i<L-1){K.next();updatePraesInfo();}else{_praesAutoStop();}},4000);}
  if(autoBtn)autoBtn.onclick=function(){if(autoOn)_praesAutoStop();else startAuto();};
  /* manuelle Navigation stoppt Auto */
  var _origNext=nextBtn.onclick;nextBtn.onclick=function(){if(_praesAutoStop)_praesAutoStop();if(_origNext)_origNext();};
  var _origPrev=prevBtn.onclick;prevBtn.onclick=function(){if(_praesAutoStop)_praesAutoStop();if(_origPrev)_origPrev();};
  _praesKeyHandler=function(e){if(e.key==='ArrowRight'||e.key===' '){e.preventDefault();if(K)K.next();updatePraesInfo();}else if(e.key==='ArrowLeft'){e.preventDefault();if(K)K.prev();updatePraesInfo();}else if(e.key==='Escape'){stopPraesentation();}};
  document.addEventListener('keydown',_praesKeyHandler);
}
/* Wischen: einmalig registriert (kein Listener-Leak bei mehrfachem Start) */
(function(){var sx=0;
  document.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
  document.addEventListener('touchend',function(e){var dx=e.changedTouches[0].clientX-sx;var K=window.KOMP;if(Math.abs(dx)>50&&document.body.classList.contains('praesentation')&&K){if(dx<0)K.next();else K.prev();updatePraesInfo();}},{passive:true});
})();
function stopPraesentation(){togglePraesentation(false);if(_praesKeyHandler){document.removeEventListener('keydown',_praesKeyHandler);_praesKeyHandler=null;}if(_praesAutoStop)_praesAutoStop();}
var praesBtn=document.getElementById('praesBtn');if(praesBtn)praesBtn.addEventListener('click',function(){var mm=document.getElementById('mehrmenu');if(mm)mm.hidden=true;var mb=document.getElementById('mehr');if(mb)mb.setAttribute('aria-expanded','false');startPraesentation();});
// hook pagechange to update info
window.addEventListener('kompendium:pagechange',function(){if(document.body.classList.contains('praesentation'))updatePraesInfo();});

/* PWA-Erweiterungen v2.9.5: Update-Toast, Install-Hinweis, Offline-Banner, Tasten, History */
(function () {
  'use strict';

  function ensure(id, cls, txt) {
    var el = document.getElementById(id);
    if (el) return el;
    el = document.createElement(el ? 'div' : 'div');
    el.id = id;
    if (cls) el.className = cls;
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    if (txt) el.textContent = txt;
    (document.body || document.documentElement).appendChild(el);
    return el;
  }

  /* CSS einmalig einfügen (Token-basiert) */
  var styleId = 'pwa-ext-style';
  if (!document.getElementById(styleId)) {
    var st = document.createElement('style');
    st.id = styleId;
    st.textContent =
      '#pwaToast{position:fixed;left:50%;bottom:max(1rem,env(safe-area-inset-bottom));transform:translateX(-50%);' +
      'background:var(--hdr);color:var(--btnfg);padding:.6rem .9rem;border-radius:var(--r);z-index:10001;display:none;' +
      'align-items:center;gap:.6rem;box-shadow:0 4px 14px var(--veil);font-size:.95rem;max-width:calc(100vw - 2rem)}' +
      '#pwaToast.show{display:flex}' +
      '#pwaToast .tbtn{border:0;border-radius:var(--r-sm);background:var(--btnfg);color:var(--btnbg);font:inherit;font-weight:600;' +
      'padding:.35rem .7rem;cursor:pointer;touch-action:manipulation}' +
      '#offlineBanner{position:fixed;top:0;left:0;right:0;z-index:10000;background:var(--warnbg);color:var(--warnfg);' +
      'border-bottom:1px solid var(--warn);padding:.4rem .6rem;text-align:center;font-size:.9rem;display:none}' +
      '#offlineBanner.show{display:block}' +
      'body.praesentation #offlineBanner{display:none!important}';
    document.head.appendChild(st);
  }

  /* SW-Update-Toast */
  var toast = null, toastTimer = null;
  function showToast(txt, btnTxt, cb) {
    if (!toast) {
      toast = ensure('pwaToast', null, '');
      toast.setAttribute('role', 'alert');
    }
    toast.textContent = '';
    var sp = document.createElement('span'); sp.textContent = txt; toast.appendChild(sp);
    if (btnTxt && cb) {
      var b = document.createElement('button'); b.type = 'button'; b.className = 'tbtn';
      b.textContent = btnTxt; b.addEventListener('click', function () { hideToast(); cb(); });
      toast.appendChild(b);
    }
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(hideToast, 30000);
  }
  function hideToast() { if (toast) toast.classList.remove('show'); }
  window.addEventListener('pwa:update-ready', function () {
    showToast('Es gibt eine neue Version.', 'Jetzt aktualisieren', function () {
      if (navigator.serviceWorker && navigator.serviceWorker.controller) {
        navigator.serviceWorker.addEventListener('controllerchange', function () { location.reload(); });
        navigator.serviceWorker.controller.postMessage('skip-waiting');
        setTimeout(function () { location.reload(); }, 1200);
      } else location.reload();
    });
  });

  /* Install-Hinweis (Chrome/Edge) */
  var deferredPrompt = null, installShown = false;
  window.addEventListener('beforeinstallprompt', function (e) {
    e.preventDefault(); deferredPrompt = e;
    if (installShown) return;
    try { if (localStorage.getItem('anfoevo_install_hint') === 'done') return; } catch (err) {}
    installShown = true;
    setTimeout(function () {
      showToast('Als App installieren – offline nutzbar.', 'Installieren', function () {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function (c) {
          if (c && c.outcome === 'accepted') { try { localStorage.setItem('anfoevo_install_hint', 'done'); } catch (err) {} }
        }).catch(function () {});
        deferredPrompt = null;
      });
    }, 4000);
  });
  window.addEventListener('appinstalled', function () { hideToast(); });

  /* Offline-Banner */
  var banner = null;
  function offlineUI() {
    if (!banner) { banner = ensure('offlineBanner', null, ''); }
    banner.textContent = document.body.classList.contains('praesentation') ? '' : 'Keine Internetverbindung – Inhalte werden offline bereitgestellt.';
    banner.classList.toggle('show', !navigator.onLine && !document.body.classList.contains('praesentation'));
  }
  window.addEventListener('offline', offlineUI);
  window.addEventListener('online', offlineUI);
  document.addEventListener('kompendium:pagechange', offlineUI);
  offlineUI();

  /* Home/End blättern */
  document.addEventListener('keydown', function (e) {
    if (e.defaultPrevented) return;
    var t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || (t.isContentEditable))) return;
    var K = window.KOMP;
    if (!K) return;
    if (e.key === 'Home') { K.goTo(0); e.preventDefault(); }
    else if (e.key === 'End') { K.goTo((K.list() || []).length - 1); e.preventDefault(); }
  });

  /* History: pushState pro Seite, Back = vorherige Seite */
  try {
    var lastHash = null;
    window.addEventListener('kompendium:pagechange', function () {
      var h = location.hash;
      if (h && h !== lastHash) { lastHash = h; }
    });
    window.addEventListener('popstate', function () {
      var K = window.KOMP;
      if (!K) return;
      var m = location.hash.match(/^#p=([\s\S]+)$/);
      if (m) {
        var id = decodeURIComponent(m[1]);
        if (id !== (K.current && K.current())) K.goToId(id);
      }
    });
  } catch (e) {}
})();
