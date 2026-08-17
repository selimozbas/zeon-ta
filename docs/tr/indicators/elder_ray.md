# Elder Ray (Boğa Gücü / Ayı Gücü)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/elder_ray.md)

`zeonta.elder_ray()` — Bull Power / Bear Power — the day's high and low measured against an EMA.

## Ne ölçer

Alexander Elder tarafından, her bir barın içine, yalnızca nerede kapandığına değil, geçerli trende göre bakmanın bir yolu olarak geliştirildi. Boğa Gücü, alıcıların bar içinde fiyatı EMA'nın ne kadar üzerine itebildiğini okur; Ayı Gücü, satıcıların onu ne kadar altına ittiğini okur. Tek bir kapanış-fiyatı karşılaştırması yerine bar başına iki sayı, barın *içinde* yaşanan çekişmeyi yakalar; bu, kapanışın tek başına sildiği bir bilgidir.

## Formül

```text
EMA = EMA(Kapanış, uzunluk); Boğa Gücü = Yüksek - EMA; Ayı Gücü = Düşük - EMA
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `13` |

## Döndürdükleri

| Kolon |
| --- |
| `BULLP_13` |
| `BEARP_13` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.elder_ray(df['high'], df['low'], df['close']).tail(3)
```

```text
            BULLP_13  BEARP_13
date                          
2024-10-25  0.303033 -0.759267
2024-10-26 -0.081543 -1.227343
2024-10-27 -0.420822 -1.987922
```

**Accessor biçimi:** `df.zta.elder_ray(...)`

## Nasıl okunur

Sağlıklı bir yükseliş trendinde, Boğa Gücü pozitif kalırken Ayı Gücü negatif kalır ama bar bar sıfıra doğru küçülür — satıcılar geri çekilmeler sırasında bile hakimiyetini kaybediyordur. EMA'nın kendisi hâlâ yükselirken Ayı Gücü'nün pozitife dönmesi ya da Boğa Gücü'nün negatife dönmesi, trendin barın kontrolünü kaybettiğine ve bir dönüşün yakın olabileceğine dair klasik Elder Ray uyarısıdır.

## Dikkat edilmesi gerekenler

Sabit, hızlanmayan bir trendde, EMA'nın kendi sabit gecikmesi barın yüksek-düşük aralığını aşabilir; bu da trendde aslında hiçbir şey değişmemişken bile Ayı Gücü'nü (yükseliş trendinde) pozitife ya da Boğa Gücü'nü (düşüş trendinde) negatife çevirir — bu, gecikmeli bir EMA'nın fiyatın ne kadar gerisinde kaldığının gerçek bir özelliğidir, zayıflık sinyali değildir. Elder'ın kendi kuralı iki çizgiyi EMA'nın eğimiyle *birlikte* okur, Boğa ya da Ayı Gücü'nü asla tek başına değil.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000717955-bull-bear-power/](https://www.tradingview.com/support/solutions/43000717955-bull-bear-power/)
