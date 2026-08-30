# İvme Bantları (Acceleration Bands)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/accbands.md)

`zeonta.accbands()` — SMA envelope of High/Low scaled by their own range, widening with volatility.

## Ne ölçer

Price Headley'nin oynaklık zarfı: [bbands](bbands.md)'ın aksine (sabit bir çarpanı *yuvarlanan* standart sapmayla ölçekler), buradaki genişleme her bir barın *kendi* yüksek-düşük aralığından gelir — tek büyük bir bar, bir sapma penceresinden gecikme olmaksızın bantları anında birbirinden uzaklaştırır.

## Formül

```text
Oran = c*(Yüksek-Düşük)/(Yüksek+Düşük); Üst=SMA(Yüksek*(1+Oran),n); Alt=SMA(Düşük*(1-Oran),n); Orta=SMA(Kapanış,n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |
| `c` | `4.0` |

## Döndürdükleri

| Kolon |
| --- |
| `ACCBL_20` |
| `ACCBM_20` |
| `ACCBU_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.accbands(df['high'], df['low'], df['close']).tail(3)
```

```text
             ACCBL_20   ACCBM_20   ACCBU_20
date                                       
2024-10-25  87.553747  90.703090  93.958972
2024-10-26  87.543579  90.624895  93.875104
2024-10-27  87.307017  90.504580  93.911617
```

**Accessor biçimi:** `df.zta.accbands(...)`

## Nasıl okunur

Herhangi bir zarf gibi okunur: haftalık ya da aylık bir grafikte bantların dışında bir kapanış, Headley'nin kendi tercih ettiği kırılma sinyalidir; daha kısa zaman dilimlerinde bantlar aynı zamanda dinamik destek/direnç görevi görür.

## Dikkat edilmesi gerekenler

Sıfır-aralıklı ve sıfır-fiyatlı bir bar (Yüksek + Düşük == 0), oranı tanımsız bırakır; bantlar sıfıra bölme yerine o bar için `NaN`'a döner.

## Kaynak

Formül kaynağı: [https://help.tc2000.com/m/69445/l/755840-acceleration-bands](https://help.tc2000.com/m/69445/l/755840-acceleration-bands)
