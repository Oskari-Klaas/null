Markdown# 🎮 Null Game Project

**Null** on tempokas ja minimalistlik ellujäämismäng, mis on loodud Pythoni ja Pygame'i raamistikuga. See on mäng, kus iga sinu otsus muudab areeni ohtlikumaks.

## 📝 Ülevaade
Mängus Null juhid sa väikest ruutu pimedas ja reaktiivses keskkonnas. Sinu eesmärk on lihtne: jää ellu kuni taimeri lõpuni. Kuid mäng muutub iga roundiga raskemaks, sest sa pead ise valima oma järgmise "koormuse". Pärast iga ellujäämist pakub mäng sulle kolme uut vaenlast või "cursed" efekti – sinu valik määrab, milliseks kujuneb järgmine raund.

## ✨ Põhiomadused
* **Dünaamiline valikusüsteem:** Iga vooru lõpus valid sa ise järgmise ohu. Kas valid ennustatava Sentineli, rida vahetava Drifteri või kiire ja ohtliku Reaperi?
* **Erinevad vaenlaste arhetüübid:** Tavalised vaenlased (Jälitajad), ridade tõmbajad (Drifter) ja liikumatud valvurid.
* **Erilised ohud:** Teleporditav Reaper, pulseeriv Pulse ja ekraani läbiv The Weaver.
* **Modulaarne ülesehitus:** Mäng on jaotatud loogilisteks mooduliteks (vaenlased, mängija, kokkupõrked ja põhiloogika).

---

## 🚀 Kuidas mängu käivitada? (Alustamine)

Järgi neid samme täpselt, et vältida terminali vigu:

1. **Klooni repositoorium ja mine kausta:**
   ```bash
   git clone [https://github.com/Oskari-Klaas/null.git](https://github.com/Oskari-Klaas/null.git)
   cd null
Paigalda vajalikud teegid (Pygame):Bashpython -m pip install pygame
Käivita mäng:Bashpython maincore.py
🕹️ JuhtimineTegevusKlahvLiikumineW, A, S, DValiku kinnitamineHiireklõpsVäljumineESC📂 Projekti struktuurmaincore.py – Mängu süda: haldab tsüklit, menüüd ja helisid.player.py – Mängija füüsika ja liikumine.enemy.py – Vaenlaste tüübid ja AI.damage.py – Kokkupõrgete tuvastamine ja elud.👥 AutoridProjekt valmis meeskonnatööna:Renald Mattias Kronbergs – Mänguloogika, vaenlaste AI ja arendus.Oskari Klaas – Süsteemi arhitektuur, füüsika ja Git-i haldus.Reivo Meedla – Helikujundus ja visuaalsed efektid.🛠️ Veatuvastus (Troubleshooting)Kui python käsk ei tööta, proovi kasutada py või python3.Veendu, et oled terminalis õiges kaustas (cd null) enne käivitamist.
