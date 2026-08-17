# Para Akışı Endeksi (MFI)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/mfi.md)

`zeonta.mfi()` — "Volume-weighted RSI" — momentum measured through money flow instead of price.

## Ne ölçer

[rsi](rsi.md)'nin tam mekanizmasını alın — bir pencere boyunca toplanan kazanç ve kayıplar, 0-100 ölçeğine sıkıştırılır — ve "fiyat değişimi"ni "tipik fiyat çarpı hacim" ile değiştirin. Sonuç, RSI'nin cevaplayamayacağı bir soruyu cevaplar: bu hareket gerçek bir katılımla mı destekleniyordu, yoksa ince bir hacimde mi gerçekleşti?

## Formül

```text
Tipik Fiyat = (Yüksek + Düşük + Kapanış) / 3; Ham Para Akışı = Tipik Fiyat x Hacim; Para Akışı Oranı = Toplam(Pozitif Para Akışı, n) / Toplam(Negatif Para Akışı, n); MFI = 100 - 100 / (1 + Para Akışı Oranı)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `MFI_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14).tail(3)
```

```text
date
2024-10-25    31.570060
2024-10-26    24.899728
2024-10-27    25.350635
Name: MFI_14, dtype: float64
```

**Accessor biçimi:** `df.zta.mfi(...)`

## Nasıl okunur

0-100 ölçeğini tam olarak RSI gibi okuyun — geleneksel olarak 80'in üstü "aşırı alım", 20'nin altı "aşırı satım" — ama RSI ile uyuşmayan bir MFI okumasını daha bilgilendirici sinyal olarak değerlendirin: bu, hareketin arkasındaki hacmin fiyat hareketiyle uyuşmadığı anlamına gelir.

## Dikkat edilmesi gerekenler

RSI'nin Wilder-yumuşatılmış ortalamalarının aksine, MFI pozitif ve negatif akışı sade (yumuşatılmamış) bir kayan pencereyle toplar; bu yüzden aynı uzunlukta RSI'den bar bara daha gürültülü olabilir. Ayrıca RSI'nin temel uyarısını da devralır: "aşırı alım" bir satış talimatı değil, momentumun bir tarifidir — güçlü bir trend MFI'yi haftalarca 80'in üstünde tutabilir.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/money-flow-index-mfi)
