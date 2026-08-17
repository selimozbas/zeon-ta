# Chaikin Para Akışı (CMF)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/cmf.md)

`zeonta.cmf()` — Volume-weighted measure of where price closed within its own range.

## Ne ölçer

[obv](obv.md)'nin daha özenli kuzeni: yalnızca kapanışın yukarı mı aşağı mı olduğunu sormak yerine, CMF kapanışın *barın tüm aralığının neresine* düştüğünü sorar ve bu konumu hacimle ağırlıklandırır. Aralığın tepesine yapışan bir kapanış +1'e yakın puan alır; dibine yapışan bir kapanış -1'e yakın puan alır.

## Formül

```text
Para Akışı Çarpanı = ((Kapanış - Düşük) - (Yüksek - Kapanış)) / (Yüksek - Düşük); Para Akışı Hacmi = Para Akışı Çarpanı x Hacim; CMF = Toplam(Para Akışı Hacmi, n) / Toplam(Hacim, n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `CMF_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cmf(df['high'], df['low'], df['close'], df['volume'], length=20).tail(3)
```

```text
date
2024-10-25   -0.155522
2024-10-26   -0.202660
2024-10-27   -0.226028
Name: CMF_20, dtype: float64
```

**Accessor biçimi:** `df.zta.cmf(...)`

## Nasıl okunur

Pencere boyunca sürekli sıfırın üstünde kalan okumalar, hacmin güçlü kapanan barlarda yoğunlaştığı — alım baskısı — anlamına gelir. Yatırımcılar genelde belirli seviyelerde işlem yapmak yerine sıfır çizgisinin kendisini bir trend filtresi olarak kullanır ("yalnızca CMF pozitifken uzun pozisyon al" gibi).

## Dikkat edilmesi gerekenler

Çok dar bir yüksek-düşük aralığına sahip bir bar, Para Akışı Çarpanı'nın paydasını küçültür; bu yüzden sakin bir bardaki sıradan hacim, aslında pek bir şey olmamasına rağmen CMF'yi sert sallayabilir — bu uygulama, patlamasına izin vermek yerine bu dejenere durumu `0` olarak tanımlar, ama art arda gelen dar aralıklı barlar CMF'yi altındaki fiyat hareketinin önerdiğinden daha gürültülü hâle getirebilir.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/chaikin-money-flow-cmf)
