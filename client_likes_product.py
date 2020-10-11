import os
import pandas as pd
import numpy as np
from misc import cached


os.chdir('data')


purchases = pd.concat([pd.read_csv(filename)[['user_id', 'order_id', 'product_id', 'price']] for filename in os.listdir('.') if "tab_2" in filename])
products = purchases[['product_id', 'price']].drop_duplicates()
purchases = purchases[['user_id', 'order_id', 'product_id']]


orders = pd.read_csv("tab_1_orders.csv")[["order_id", "order_created_time"]]
purchases = purchases.merge(orders, how='inner')


@cached
def get_price(item):
  return products[products.product_id == item]["price"].mean()


@cached
def num_purchases(client, item):
  return len(purchases[(purchases.product_id == item) & (purchases.user_id == client)]["order_created_time"].drop_duplicates())


@cached
def median_interval(client, item, threshold=3):
  purchase_history = purchases[purchases.product_id == item][["order_created_time", "user_id"]]
  relevant_history = purchase_history[purchase_history.user_id == client]["order_created_time"]
  relevant_history = pd.to_datetime(relevant_history).drop_duplicates()
  assert len(relevant_history) > threshold
  relevant_history = relevant_history.sort_values()
  relevant_history = relevant_history[1:].reset_index(drop=True) - relevant_history[:-1].reset_index(drop=True)
  return relevant_history.median() / pd.Timedelta(days=1)


@cached
def peculiar_interval(item, threshold=3, tolerance=0.8):
  purchase_history = purchases[purchases.product_id == item][["order_created_time", "user_id"]]
  relevant_users = purchase_history["user_id"].unique()
  median_intervals = []
  for client in relevant_users:
    try:
      median_intervals.append(median_interval(client, item, threshold=threshold)) # sucks
    except AssertionError:
      pass

  return np.quantile(median_intervals, tolerance)


def is_item_consumable(item, price_threshold=1000):
  return get_price(item) < price_threshold

def client_likes_item(client, item, threshold=3): 
  if is_item_consumable(item):
    if num_purchases(client, item) <= threshold:
      return 0.0
    else:
      return float(peculiar_interval(item, threshold=threshold) > median_interval(client, item))
  else:
    return float(num_purchases(client, item) > 0)

