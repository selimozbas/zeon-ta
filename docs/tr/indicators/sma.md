# Basit Hareketli Ortalama (SMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/sma.md)

`zeonta.sma()` — Equally weighted average of the last n closes.

## Ne ölçer

Gürültünün içinden trendi görmenin en basit yolu: son n kapanışın ortalamasını alıp fiyat yerine onu çizmek. Penceredeki her bar eşit sayılır; bu da SMA'yı yumuşak ve öngörülebilir kılar — ama aynı zamanda tek bir eski barın pencereden çıkması bile onu hareket ettirebilir.

## Formül

```text
SMA(n) = (1/n) x toplam(Kapanış[i]), son n bar için — son n kapanışın eşit ağırlıklı ortalaması.
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `SMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.sma(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.703090
2024-10-26    90.624895
2024-10-27    90.504580
Name: SMA_20, dtype: float64
```

```python
df.zta.sma(50).tail(3)
```

```text
date
2024-10-25    91.545918
2024-10-26    91.470696
2024-10-27    91.385108
Name: SMA_50, dtype: float64
```

**Accessor biçimi:** `df.zta.sma(...)`

## Nasıl okunur

Yükselen bir SMA'nın üzerindeki fiyat ders kitabı yükseliş trendidir; düşen bir SMA'nın altındaki fiyat ise düşüş trendidir. 50 ve 200, diğer tüm uzunluklardan çok daha fazla izlenir — sırf çok sayıda kişi onları izlediği için.

## Dikkat edilmesi gerekenler

SMA yaklaşık uzunluğunun yarısı kadar gecikir, yani bir dönüşü gerçekleştikten çok sonra teyit eder; geleceğin tahmini değil, geçmişin tarifidir. Yatay piyasada fiyat onu sürekli keser ve tamamı gürültü olan sinyaller üretir.

## Kaynak

Formül kaynağı: [https://ta.cognicode.org/learn/sma](https://ta.cognicode.org/learn/sma)
