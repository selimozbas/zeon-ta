# Bollinger Bantları

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/bbands.md)

`zeonta.bbands()` — SMA envelope scaled by standard deviation; width tracks volatility.

## Ne ölçer

Genişliği son dönem oynaklığı tarafından belirlenen bir zarfa sahip hareketli ortalama. Piyasa sakinleştiğinde bantlar içeri sıkışır; sertleştiğinde dışarı açılır. Kendini ayarlayan bu genişlik işin bütün püf noktasıdır.

## Formül

```text
Orta Bant = HO(Kapanış, 20); Üst Bant = Orta + 2 x StandartSapma(Kapanış, 20); Alt Bant = Orta - 2 x StandartSapma(Kapanış, 20)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |
| `std` | `2.0` |
| `ddof` | `0` |

## Döndürdükleri

| Kolon |
| --- |
| `BBL_20_2.0` |
| `BBM_20_2.0` |
| `BBU_20_2.0` |
| `BBB_20_2.0` |
| `BBP_20_2.0` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.bbands(df['close'], length=20, std=2).tail(3)
```

```text
            BBL_20_2.0  BBM_20_2.0  BBU_20_2.0  BBB_20_2.0  BBP_20_2.0
date                                                                  
2024-10-25   89.262603   90.703090   92.143577    0.031763    0.289346
2024-10-26   89.027293   90.624895   92.222497    0.035257    0.028701
2024-10-27   88.661008   90.504580   92.348152    0.040740   -0.048495
```

**Accessor biçimi:** `df.zta.bbands(...)`

## Nasıl okunur

Sıkışmayı izlemek için bakılacak sayı `BBB`'dir (bant genişliği) — bant genişliğinde aylık dip, büyük hareketlerin çoğundan önce gelir. `BBP` (yüzde-B) fiyatın bantların neresinde olduğunu verir: `0` alt bant, `1` üst banttır; `0..1` dışındaki değerler fiyatın bantların ötesinde kapandığını gösterir.

## Dikkat edilmesi gerekenler

Üst banda değmek satış sinyali değildir. Güçlü bir trendde fiyat "bandı yürür" ve onlarca bar boyunca ona yaslanır — Bollinger'ın kendisi bantların bir işlem sistemi değil, göreceli yüksek-düşük ölçüsü olduğunu söylemiştir. Ayrıca buradaki standart sapma, grafik platformlarıyla uyumlu olacak şekilde anakütle sapmasıdır (`ddof=0`).

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/bollinger-bands](https://ta.cognicode.org/learn/bollinger-bands)
