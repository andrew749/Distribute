var a = [];
for (var x in payload_data) {
  a.push(parseInt(payload_data[x]));
}
return a;
