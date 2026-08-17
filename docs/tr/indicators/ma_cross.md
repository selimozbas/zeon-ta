# Hareketli Ortalama Kesişimleri

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ma_cross.md)

`zeonta.ma_cross()` — Fast/slow moving-average crossover signals (golden and death cross).

## Ne ölçer

Farklı uzunlukta iki ortalama ve yer değiştirdikleri her an bir sinyal. 50/200 çiftinin meşhur isimleri vardır — altın kesişim ve ölüm kesişimi — ve finans basınında haber olur; piyasayı hareket ettirmesinin bir sebebi de budur.

## Formül

```text
Yükseliş yönlü kesişim (hızlı=50, yavaş=200 olduğunda altın kesişim): hızlıHO[i-1] <= yavaşHO[i-1] ve hızlıHO[i] > yavaşHO[i]. Düşüş yönlü kesişim (ölüm kesişimi): hızlıHO[i-1] >= yavaşHO[i-1] ve hızlıHO[i] < yavaşHO[i].
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `50` |
| `slow` | `200` |
| `mode` | `'sma'` |

## Döndürdükleri

| Kolon |
| --- |
| `MAfast_50` |
| `MAslow_200` |
| `cross_50_200` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ma_cross(df['close'], fast=20, slow=50).query('cross_20_50 != 0').tail(3)
```

```text
            MAfast_20  MAslow_50  cross_20_50
date                                         
2024-06-29  96.420760  96.434442         -1.0
2024-07-11  97.134010  97.088798          1.0
2024-07-20  96.591125  96.678434         -1.0
```

**Accessor biçimi:** `df.zta.ma_cross(...)`

## Nasıl okunur

`cross` kolonu, hızlı ortalamanın yavaşın üstüne çıktığı barda `1.0`, altına indiği barda `-1.0`, diğer barlarda `0.0` değerini alır. Birçok yatırımcı kesişimi giriş tetikleyicisi olarak değil, rejim filtresi olarak kullanır — yalnızca hızlı ortalama üstteyken uzun pozisyon açmak gibi.

## Dikkat edilmesi gerekenler

Her iki girdi de geciktiği için kesişim iki kat gecikir: altın kesişim oluştuğunda hareketin büyük kısmı genellikle geride kalmıştır. Yatay bantta çift sürekli ileri geri keser ve her birini mekanik olarak işleme sokmak para kaybettirir.
