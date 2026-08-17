# Hacim Temelleri

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/relative_volume.md)

`zeonta.relative_volume()` — Volume moving average and relative volume (today versus normal).

## Ne ölçer

Ham hacim tek başına neredeyse anlamsızdır — bir milyon lot bir hisse için devasa, bir başkası için yuvarlama hatasıdır. Son dönem ortalamasına bölmek onu her yerde aynı şeyi ifade eden bir sayıya çevirir: bu bar normale kıyasla ne kadar yoğun?

## Formül

```text
Hacim HO(n) = (1/n) x toplam(Hacim[i]), son n bar için (fiyat yerine hacme uygulanan basit hareketli ortalama). Göreceli hacim = mevcut barın Hacmi / Hacim HO(n).
```

## Parametreler

**Gerekli girdiler:** `volume`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `VOLMA_20` |
| `RVOL_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.relative_volume(df['volume'], length=20).tail(3)
```

```text
             VOLMA_20   RVOL_20
date                           
2024-10-25  514563.25  1.445869
2024-10-26  500691.60  0.739206
2024-10-27  480908.10  0.546788
```

**Accessor biçimi:** `df.zta.relative_volume(...)`

## Nasıl okunur

`RVOL` değerinin 1,0 olması tamamen sıradan bir bardır; 2,0 son dönem normalinin iki katıdır. Yüksek göreceli hacimle gelen bir kırılımın arkasında katılım vardır; aynı kırılım 0,5 ile geliyorsa çok az kişi tarafından yapılıyordur ve genelde kalıcı olmaz.

## Dikkat edilmesi gerekenler

Göreceli hacim planlı olaylar çevresinde bozulur — endeks yeniden dengelemeleri, opsiyon vadeleri ve bilanço açıklamaları, inanç hakkında hiçbir şey söylemeyen çok yüksek değerler üretir. Ayrıca her seansın açılış ve kapanışında yüksek seyreder; benzeri benzerle karşılaştırın.
