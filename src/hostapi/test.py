import re
from underscore import Underscore as _

data = [
  {
    "operation_id": "01074b18-4bdb-11e9-ace0-002590ea2218",
    "transaction_id": "010a7f22-4bdb-11e9-997f-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "01074b18-4bdb-11e9-ace0-002590ea2218",
    "transaction_id": "0111180a-4bdb-11e9-bcdf-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "028798e6-4b1b-11e9-a697-002590569245",
    "transaction_id": "028ce1fc-4b1b-11e9-b7c1-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "028798e6-4b1b-11e9-a697-002590569245",
    "transaction_id": "02940a40-4b1b-11e9-a673-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "036d55f4-4be1-11e9-8912-0cc47a172970",
    "transaction_id": "0372e82a-4be1-11e9-8503-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "036d55f4-4be1-11e9-8912-0cc47a172970",
    "transaction_id": "037e462a-4be1-11e9-85f6-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "04ce339c-4bdb-11e9-98b5-002590ea2218",
    "transaction_id": "04d0948e-4bdb-11e9-b8e2-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "04d3fc54-4bc3-11e9-beba-0cc47a172970",
    "transaction_id": "04d63668-4bc3-11e9-8e93-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "04ce339c-4bdb-11e9-98b5-002590ea2218",
    "transaction_id": "04d6b1f2-4bdb-11e9-bfdd-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "04d3fc54-4bc3-11e9-beba-0cc47a172970",
    "transaction_id": "04dc1e48-4bc3-11e9-9af4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "05163870-4bce-11e9-b977-002590ea2218",
    "transaction_id": "0518801c-4bce-11e9-b69c-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "05163870-4bce-11e9-b977-002590ea2218",
    "transaction_id": "05526c14-4bce-11e9-91be-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "056cdbc4-4bcb-11e9-aabb-0cc47a172970",
    "transaction_id": "056f3e5a-4bcb-11e9-9cbe-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "056cdbc4-4bcb-11e9-aabb-0cc47a172970",
    "transaction_id": "0575c0a4-4bcb-11e9-b49d-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "07bd0de8-4af6-11e9-b417-002590569245",
    "transaction_id": "07bef8c4-4af6-11e9-9444-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "07bd0de8-4af6-11e9-b417-002590569245",
    "transaction_id": "07c78f34-4af6-11e9-bae8-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "098b2146-4bdc-11e9-b7bc-002590ea2218",
    "transaction_id": "098e369c-4bdc-11e9-a5fa-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "098b2146-4bdc-11e9-b7bc-002590ea2218",
    "transaction_id": "0997446c-4bdc-11e9-bb8f-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "098b2146-4bdc-11e9-b7bc-002590ea2218",
    "transaction_id": "099c270c-4bdc-11e9-87c7-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "0b5489f2-4b07-11e9-84c6-002590569245",
    "transaction_id": "0b567a14-4b07-11e9-a8df-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "0fbbe4f4-4bbb-11e9-9dff-0cc47a172970",
    "transaction_id": "0fbdcf26-4bbb-11e9-a3fe-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "1211735a-4bd8-11e9-a67b-0cc47a172970",
    "transaction_id": "1213cb3c-4bd8-11e9-8c75-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "1211735a-4bd8-11e9-a67b-0cc47a172970",
    "transaction_id": "1219a03e-4bd8-11e9-87e6-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "129a0248-4be1-11e9-8578-002590ea2218",
    "transaction_id": "129c8b30-4be1-11e9-b9b9-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "129a0248-4be1-11e9-8578-002590ea2218",
    "transaction_id": "12b3d42a-4be1-11e9-aaed-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "1465d664-4bdd-11e9-9d9b-0cc47a172970",
    "transaction_id": "1467df54-4bdd-11e9-9f98-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "1465d664-4bdd-11e9-9d9b-0cc47a172970",
    "transaction_id": "14706476-4bdd-11e9-9260-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "1465d664-4bdd-11e9-9d9b-0cc47a172970",
    "transaction_id": "14748074-4bdd-11e9-856d-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "158f4778-4bbf-11e9-b68b-002590ea2218",
    "transaction_id": "1591f0d6-4bbf-11e9-a0ad-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "158f4778-4bbf-11e9-b68b-002590ea2218",
    "transaction_id": "159c1340-4bbf-11e9-99cd-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "171bcb28-4bd5-11e9-b497-002590ea2218",
    "transaction_id": "171e3c46-4bd5-11e9-8cbd-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "171bcb28-4bd5-11e9-b497-002590ea2218",
    "transaction_id": "1724d04c-4bd5-11e9-9e8a-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "171bcb28-4bd5-11e9-b497-002590ea2218",
    "transaction_id": "17297fd4-4bd5-11e9-9a1c-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "17e13b14-4bd1-11e9-9b8b-0cc47a172970",
    "transaction_id": "17e30f3e-4bd1-11e9-a65a-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "17e13b14-4bd1-11e9-9b8b-0cc47a172970",
    "transaction_id": "17eaa910-4bd1-11e9-9739-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "1ab0caae-4afe-11e9-b50c-002590569245",
    "transaction_id": "1ab372cc-4afe-11e9-b885-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "1ae1cf6c-4bdc-11e9-9829-002590ea2218",
    "transaction_id": "1ae47028-4bdc-11e9-9176-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "1ae1cf6c-4bdc-11e9-9829-002590ea2218",
    "transaction_id": "1aee05a2-4bdc-11e9-a9fa-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "1ae1cf6c-4bdc-11e9-9829-002590ea2218",
    "transaction_id": "1af2d0fa-4bdc-11e9-a3ff-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "1b5207b2-4bd9-11e9-ab5b-002590ea2218",
    "transaction_id": "1b545634-4bd9-11e9-99dd-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "1b5207b2-4bd9-11e9-ab5b-002590ea2218",
    "transaction_id": "1b5c7800-4bd9-11e9-b17a-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "1b5207b2-4bd9-11e9-ab5b-002590ea2218",
    "transaction_id": "1b60db0c-4bd9-11e9-9092-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "1d177570-4bc3-11e9-b901-0cc47a172970",
    "transaction_id": "1d193b08-4bc3-11e9-a217-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "1d177570-4bc3-11e9-b901-0cc47a172970",
    "transaction_id": "1d1f031c-4bc3-11e9-b9ad-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "1e2651cc-4bcb-11e9-bd30-0cc47a172970",
    "transaction_id": "1e283866-4bcb-11e9-834b-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "1e2651cc-4bcb-11e9-bd30-0cc47a172970",
    "transaction_id": "1e2dac9c-4bcb-11e9-a7e4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "1e678f28-4bd2-11e9-8a64-0cc47a172970",
    "transaction_id": "1e68fa84-4bd2-11e9-9dbc-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "1e678f28-4bd2-11e9-8a64-0cc47a172970",
    "transaction_id": "1e70c9d0-4bd2-11e9-a405-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "2011cf64-4afb-11e9-8462-002590569245",
    "transaction_id": "20137a30-4afb-11e9-9b10-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "254a72ee-4bbc-11e9-93bf-0cc47a172970",
    "transaction_id": "254caafa-4bbc-11e9-a172-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "2568ef46-4b06-11e9-820f-002590569245",
    "transaction_id": "256b7702-4b06-11e9-bad4-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "254a72ee-4bbc-11e9-93bf-0cc47a172970",
    "transaction_id": "2575168e-4bbc-11e9-96eb-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "28c6e81a-4bd2-11e9-9399-0cc47a172970",
    "transaction_id": "28cb770e-4bd2-11e9-8d07-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "2931348e-4bc0-11e9-b8a1-002590ea2218",
    "transaction_id": "29336a2e-4bc0-11e9-af5c-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "2931348e-4bc0-11e9-b8a1-002590ea2218",
    "transaction_id": "294b6dd6-4bc0-11e9-9668-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "2ad11c76-4bbd-11e9-a594-002590ea2218",
    "transaction_id": "2ad3d9e8-4bbd-11e9-ab1a-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "2ad11c76-4bbd-11e9-a594-002590ea2218",
    "transaction_id": "2adca2da-4bbd-11e9-a5f6-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "2cae6ffc-4bb9-11e9-94ae-002590569245",
    "transaction_id": "2cb2b792-4bb9-11e9-a580-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "2cae6ffc-4bb9-11e9-94ae-002590569245",
    "transaction_id": "2cbea2fa-4bb9-11e9-aad9-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "2cae6ffc-4bb9-11e9-94ae-002590569245",
    "transaction_id": "2cc49f0c-4bb9-11e9-b9f2-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "2e3aa0a2-4afb-11e9-a6d1-002590569245",
    "transaction_id": "2e3c6950-4afb-11e9-b5e1-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "2edb61e2-4af9-11e9-b9e2-002590569245",
    "transaction_id": "2eddcd4c-4af9-11e9-88c2-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "32208a5e-4bbb-11e9-bb1f-0cc47a172970",
    "transaction_id": "3221fede-4bbb-11e9-8155-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "33c571aa-4bd2-11e9-b159-0cc47a172970",
    "transaction_id": "33c74b60-4bd2-11e9-a97f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "351a48bc-4bd4-11e9-9ad4-0cc47a172970",
    "transaction_id": "351c6b1a-4bd4-11e9-b2e5-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "351a48bc-4bd4-11e9-9ad4-0cc47a172970",
    "transaction_id": "352551da-4bd4-11e9-8a33-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "355b6b52-4bc6-11e9-a783-002590ea2218",
    "transaction_id": "355dc4a6-4bc6-11e9-bfda-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "369f89b6-4bdb-11e9-b855-0cc47a172970",
    "transaction_id": "36a1512e-4bdb-11e9-ac97-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "369f89b6-4bdb-11e9-b855-0cc47a172970",
    "transaction_id": "36aa6f48-4bdb-11e9-85cc-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "37e56132-4bd2-11e9-8fea-0cc47a172970",
    "transaction_id": "37e879e4-4bd2-11e9-8d17-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "37fe6fd4-4bbd-11e9-b23a-002590ea2218",
    "transaction_id": "37ff95c6-4bbd-11e9-8f33-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "385f4890-4bc2-11e9-948d-0cc47a172970",
    "transaction_id": "3861735e-4bc2-11e9-b822-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "385f4890-4bc2-11e9-948d-0cc47a172970",
    "transaction_id": "386f7620-4bc2-11e9-958f-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "388561e8-4bbc-11e9-83f6-002590ea2218",
    "transaction_id": "3886c4d4-4bbc-11e9-91c7-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "388561e8-4bbc-11e9-83f6-002590ea2218",
    "transaction_id": "388d7298-4bbc-11e9-b14b-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "3a1ab23e-4bc0-11e9-a27d-0cc47a172970",
    "transaction_id": "3a20b4f4-4bc0-11e9-813b-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "3a1ab23e-4bc0-11e9-a27d-0cc47a172970",
    "transaction_id": "3a274c4c-4bc0-11e9-9a5a-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "3a5d76b6-4b05-11e9-8b44-002590569245",
    "transaction_id": "3a5f41e4-4b05-11e9-ac9b-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "3b5f918c-4bbb-11e9-bfc5-002590ea2218",
    "transaction_id": "3b64d728-4bbb-11e9-978b-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "3b5f918c-4bbb-11e9-bfc5-002590ea2218",
    "transaction_id": "3b6bb9d0-4bbb-11e9-89d7-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "3c37de26-4bd3-11e9-8d90-0cc47a172970",
    "transaction_id": "3c3a41e8-4bd3-11e9-8111-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "3f4a7ce6-4bcd-11e9-be38-002590ea2218",
    "transaction_id": "3f4e466e-4bcd-11e9-af21-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "3f51c644-4b06-11e9-95d7-002590569245",
    "transaction_id": "3f539c8a-4b06-11e9-a598-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "3f4a7ce6-4bcd-11e9-be38-002590ea2218",
    "transaction_id": "3f5953ba-4bcd-11e9-82dc-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "3fccf918-4b06-11e9-933b-002590569245",
    "transaction_id": "3fcef20e-4b06-11e9-8765-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "403da690-4b06-11e9-8387-002590569245",
    "transaction_id": "403f8a78-4b06-11e9-adf5-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "40527c80-4bd5-11e9-a93f-0cc47a172970",
    "transaction_id": "40583cba-4bd5-11e9-a212-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "40527c80-4bd5-11e9-a93f-0cc47a172970",
    "transaction_id": "4061057a-4bd5-11e9-86a2-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "40a26058-4b06-11e9-bcf5-002590569245",
    "transaction_id": "40a43446-4b06-11e9-b369-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "40b59524-4b06-11e9-840d-002590569245",
    "transaction_id": "40b762c8-4b06-11e9-b103-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "416a0c20-4bd3-11e9-b562-0cc47a172970",
    "transaction_id": "416b8c08-4bd3-11e9-973e-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "416a0c20-4bd3-11e9-b562-0cc47a172970",
    "transaction_id": "4171ccee-4bd3-11e9-94a2-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "42596fe0-4b06-11e9-bbac-002590569245",
    "transaction_id": "425b48b0-4b06-11e9-853b-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "4305cd02-4ae9-11e9-a763-002590569245",
    "transaction_id": "4307f4c4-4ae9-11e9-b0fa-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "4305cd02-4ae9-11e9-a763-002590569245",
    "transaction_id": "431a0312-4ae9-11e9-a9a2-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "4325e318-4b06-11e9-b447-002590569245",
    "transaction_id": "4327cb2e-4b06-11e9-b1e5-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "43c61868-4bcb-11e9-9c90-0cc47a172970",
    "transaction_id": "43c83454-4bcb-11e9-9558-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "43c61868-4bcb-11e9-9c90-0cc47a172970",
    "transaction_id": "43d3730a-4bcb-11e9-8896-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "44d3626e-4bbd-11e9-b85b-0cc47a172970",
    "transaction_id": "44d5ae16-4bbd-11e9-8443-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "44d3626e-4bbd-11e9-b85b-0cc47a172970",
    "transaction_id": "44dc3f60-4bbd-11e9-927b-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "451f1536-4bc4-11e9-b5d3-0cc47a172970",
    "transaction_id": "45229530-4bc4-11e9-b72e-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "471026d8-4bc3-11e9-8fdd-0cc47a172970",
    "transaction_id": "47126182-4bc3-11e9-9aee-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "471026d8-4bc3-11e9-8fdd-0cc47a172970",
    "transaction_id": "4718c7f2-4bc3-11e9-965f-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "48d30fb6-4bba-11e9-bb38-0cc47a172970",
    "transaction_id": "48d4d5e4-4bba-11e9-ab24-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "48d30fb6-4bba-11e9-bb38-0cc47a172970",
    "transaction_id": "48e2a264-4bba-11e9-9a9c-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "4a8de9f4-4b04-11e9-b5f8-002590569245",
    "transaction_id": "4a8ff8a2-4b04-11e9-8f83-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "4a8de9f4-4b04-11e9-b5f8-002590569245",
    "transaction_id": "4a9a47ee-4b04-11e9-ae22-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "4aae390e-4bd9-11e9-b2ee-002590ea2218",
    "transaction_id": "4ab3a02e-4bd9-11e9-8765-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "4bd9450e-4bba-11e9-9e49-0cc47a172970",
    "transaction_id": "4bdc00a0-4bba-11e9-a5ab-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "4d092370-4afe-11e9-80c4-002590569245",
    "transaction_id": "4d0dc0f6-4afe-11e9-8a56-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "4d092370-4afe-11e9-80c4-002590569245",
    "transaction_id": "4d15323c-4afe-11e9-a95d-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "4d88ae16-4b02-11e9-b6a5-002590569245",
    "transaction_id": "4d8a6814-4b02-11e9-9500-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "4e30de96-4af9-11e9-9c89-002590569245",
    "transaction_id": "4e329c68-4af9-11e9-bd02-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "4f534a7c-4bdd-11e9-873d-0cc47a172970",
    "transaction_id": "4f55b5c8-4bdd-11e9-b2b2-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "5013cf5c-4bda-11e9-adc2-0cc47a172970",
    "transaction_id": "501608a8-4bda-11e9-8ff7-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "5013cf5c-4bda-11e9-adc2-0cc47a172970",
    "transaction_id": "501f596c-4bda-11e9-8de0-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "5043843a-4bc2-11e9-8363-0cc47a172970",
    "transaction_id": "50450814-4bc2-11e9-b7a4-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "5043843a-4bc2-11e9-8363-0cc47a172970",
    "transaction_id": "50496742-4bc2-11e9-9fe4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "5227b1e2-4b07-11e9-9dde-002590569245",
    "transaction_id": "522a26f2-4b07-11e9-81a6-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "548ff68a-4af6-11e9-a9f1-002590569245",
    "transaction_id": "5492c220-4af6-11e9-bb23-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "548ff68a-4af6-11e9-a9f1-002590569245",
    "transaction_id": "5499bc10-4af6-11e9-ac1a-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "54c75530-4b05-11e9-87a4-002590569245",
    "transaction_id": "54c923ce-4b05-11e9-8ab8-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "595583a6-4bd2-11e9-bbbd-0cc47a172970",
    "transaction_id": "59587480-4bd2-11e9-b1eb-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "5c283088-4bbe-11e9-b069-002590ea2218",
    "transaction_id": "5c2b13c0-4bbe-11e9-b1ee-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "5c283088-4bbe-11e9-b069-002590ea2218",
    "transaction_id": "5c3a0de4-4bbe-11e9-9ae8-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "5ca46f24-4bd5-11e9-9678-0cc47a172970",
    "transaction_id": "5ca638a4-4bd5-11e9-8f17-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "5d7e0448-4bc9-11e9-9eee-0cc47a172970",
    "transaction_id": "5d7ff2a8-4bc9-11e9-9861-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "5d7e0448-4bc9-11e9-9eee-0cc47a172970",
    "transaction_id": "5d870cb4-4bc9-11e9-8a62-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "5e105f26-4aea-11e9-8a23-002590569245",
    "transaction_id": "5e124aa2-4aea-11e9-969e-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "5e105f26-4aea-11e9-8a23-002590569245",
    "transaction_id": "5e1d807a-4aea-11e9-80da-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "5e105f26-4aea-11e9-8a23-002590569245",
    "transaction_id": "5e21c63a-4aea-11e9-9cab-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "5f5bb386-4bd4-11e9-836a-0cc47a172970",
    "transaction_id": "5f5d3cf6-4bd4-11e9-90ea-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "5fd408cc-4b02-11e9-af9a-002590569245",
    "transaction_id": "5fd5c81a-4b02-11e9-9366-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "608ebe5a-4af9-11e9-9069-002590569245",
    "transaction_id": "609136bc-4af9-11e9-bb7c-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "623af0da-4bc0-11e9-907d-0cc47a172970",
    "transaction_id": "623cef34-4bc0-11e9-ac74-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "623af0da-4bc0-11e9-907d-0cc47a172970",
    "transaction_id": "6243f478-4bc0-11e9-9023-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "6255c0e8-4bd1-11e9-90bc-002590ea2218",
    "transaction_id": "625878c4-4bd1-11e9-9db7-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "6255c0e8-4bd1-11e9-90bc-002590ea2218",
    "transaction_id": "6260ad32-4bd1-11e9-95ae-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "6255c0e8-4bd1-11e9-90bc-002590ea2218",
    "transaction_id": "6265ce02-4bd1-11e9-807f-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "6464bfb8-4af7-11e9-8add-002590569245",
    "transaction_id": "64675b92-4af7-11e9-ad5e-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "6464bfb8-4af7-11e9-8add-002590569245",
    "transaction_id": "64715142-4af7-11e9-aaf4-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "6563ddb0-4bc2-11e9-9700-0cc47a172970",
    "transaction_id": "65658b9c-4bc2-11e9-9c63-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "6563ddb0-4bc2-11e9-9700-0cc47a172970",
    "transaction_id": "656afe42-4bc2-11e9-b63e-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "67a9ca0a-4bd9-11e9-a1dd-0cc47a172970",
    "transaction_id": "67abf4b0-4bd9-11e9-bb56-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "67a9ca0a-4bd9-11e9-a1dd-0cc47a172970",
    "transaction_id": "67b6e78a-4bd9-11e9-881a-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "6895c836-4bc2-11e9-8fd2-0cc47a172970",
    "transaction_id": "68979ad0-4bc2-11e9-a487-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "6895c836-4bc2-11e9-8fd2-0cc47a172970",
    "transaction_id": "689d87a6-4bc2-11e9-ad64-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "6ba9001c-4bc0-11e9-a2ac-0cc47a172970",
    "transaction_id": "6baace42-4bc0-11e9-a2b9-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "6ba9001c-4bc0-11e9-a2ac-0cc47a172970",
    "transaction_id": "6bb0b05a-4bc0-11e9-8423-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "6e6205a6-4bca-11e9-91d0-002590ea2218",
    "transaction_id": "6e64f3c4-4bca-11e9-a422-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "707e5286-4bbb-11e9-b258-0cc47a172970",
    "transaction_id": "708050cc-4bbb-11e9-9976-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "707e5286-4bbb-11e9-b258-0cc47a172970",
    "transaction_id": "708861ea-4bbb-11e9-aa43-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "74835f80-4bd8-11e9-a214-002590ea2218",
    "transaction_id": "74864e8e-4bd8-11e9-abea-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "74835f80-4bd8-11e9-a214-002590ea2218",
    "transaction_id": "748d4342-4bd8-11e9-9f9b-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "74835f80-4bd8-11e9-a214-002590ea2218",
    "transaction_id": "7490c5a8-4bd8-11e9-95eb-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "75020b12-4bd0-11e9-8a59-0cc47a172970",
    "transaction_id": "7506fce4-4bd0-11e9-9a44-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "75059502-4aea-11e9-8544-002590569245",
    "transaction_id": "75078862-4aea-11e9-89fc-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "75059502-4aea-11e9-8544-002590569245",
    "transaction_id": "750e59f8-4aea-11e9-8e32-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "75020b12-4bd0-11e9-8a59-0cc47a172970",
    "transaction_id": "751320e6-4bd0-11e9-9fa9-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "75f1f8e4-4bd4-11e9-a0ea-0cc47a172970",
    "transaction_id": "75f5c21c-4bd4-11e9-805b-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "7602c95a-4bc3-11e9-81d3-0cc47a172970",
    "transaction_id": "7604e73a-4bc3-11e9-9182-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "7602c95a-4bc3-11e9-81d3-0cc47a172970",
    "transaction_id": "760a495a-4bc3-11e9-94c4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "76c5d47c-4b05-11e9-8540-002590569245",
    "transaction_id": "76c795a0-4b05-11e9-b049-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "76cfc2be-4bca-11e9-bcaf-002590ea2218",
    "transaction_id": "76d24fd4-4bca-11e9-a402-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "76cfc2be-4bca-11e9-bcaf-002590ea2218",
    "transaction_id": "76da4a54-4bca-11e9-b259-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "771b1506-4bbc-11e9-8de8-002590ea2218",
    "transaction_id": "771e3484-4bbc-11e9-8fc9-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "771b1506-4bbc-11e9-8de8-002590ea2218",
    "transaction_id": "7727b8e2-4bbc-11e9-9976-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "7735dc24-4bbc-11e9-9739-0cc47a172970",
    "transaction_id": "773756a8-4bbc-11e9-ba7a-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "788bb62a-4af9-11e9-bc74-002590569245",
    "transaction_id": "788e47be-4af9-11e9-8cb4-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "788bb62a-4af9-11e9-bc74-002590569245",
    "transaction_id": "78a7e4b2-4af9-11e9-ae1d-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "798b5c32-4bd6-11e9-a6cd-0cc47a172970",
    "transaction_id": "798e0630-4bd6-11e9-870b-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "798b5c32-4bd6-11e9-a6cd-0cc47a172970",
    "transaction_id": "799481cc-4bd6-11e9-a149-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "79bee8b0-4bde-11e9-89a2-0cc47a172970",
    "transaction_id": "79c19e02-4bde-11e9-913f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "79bee8b0-4bde-11e9-89a2-0cc47a172970",
    "transaction_id": "79ce3a5e-4bde-11e9-aa6c-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "7e32b0c0-4bca-11e9-8342-002590ea2218",
    "transaction_id": "7e37a29c-4bca-11e9-b187-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "7e32b0c0-4bca-11e9-8342-002590ea2218",
    "transaction_id": "7e3e0830-4bca-11e9-b76a-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "7f08c2a2-4bcd-11e9-aa97-002590ea2218",
    "transaction_id": "7f0be108-4bcd-11e9-9bec-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "8033fb68-4bc0-11e9-a7cd-0cc47a172970",
    "transaction_id": "8035d9a6-4bc0-11e9-908e-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8033fb68-4bc0-11e9-a7cd-0cc47a172970",
    "transaction_id": "803ca664-4bc0-11e9-8c2e-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "831996be-4bbe-11e9-85c3-002590ea2218",
    "transaction_id": "832041c6-4bbe-11e9-ad13-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "831996be-4bbe-11e9-85c3-002590ea2218",
    "transaction_id": "83290bda-4bbe-11e9-b97f-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "83c82b14-4bbb-11e9-b44e-0cc47a172970",
    "transaction_id": "83ca068c-4bbb-11e9-9b4e-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "83c82b14-4bbb-11e9-b44e-0cc47a172970",
    "transaction_id": "83cfc9be-4bbb-11e9-9677-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "84cf13c4-4bc0-11e9-86f0-0cc47a172970",
    "transaction_id": "84d0e258-4bc0-11e9-b6e5-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "84cf13c4-4bc0-11e9-86f0-0cc47a172970",
    "transaction_id": "84e11498-4bc0-11e9-9e87-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "85b085e6-4bcc-11e9-9362-0cc47a172970",
    "transaction_id": "85b7fc68-4bcc-11e9-9f0f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "85b085e6-4bcc-11e9-9362-0cc47a172970",
    "transaction_id": "85beb094-4bcc-11e9-b85f-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8667337c-4bc2-11e9-93b9-0cc47a172970",
    "transaction_id": "8668707a-4bc2-11e9-8631-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8667337c-4bc2-11e9-93b9-0cc47a172970",
    "transaction_id": "866dba30-4bc2-11e9-80d3-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "86ebe008-4bd2-11e9-999e-0cc47a172970",
    "transaction_id": "86ed648c-4bd2-11e9-b6da-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "86ebe008-4bd2-11e9-999e-0cc47a172970",
    "transaction_id": "86f31e68-4bd2-11e9-9678-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "87034c40-4bda-11e9-a8c5-0cc47a172970",
    "transaction_id": "87053b36-4bda-11e9-8894-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "87034c40-4bda-11e9-a8c5-0cc47a172970",
    "transaction_id": "870b4bde-4bda-11e9-9790-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "888139ce-4b03-11e9-bb2d-002590569245",
    "transaction_id": "8883a34e-4b03-11e9-ae0c-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "88af9018-4b1b-11e9-8c95-002590569245",
    "transaction_id": "88b21824-4b1b-11e9-818c-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "8a875cca-4bbd-11e9-a4cd-0cc47a172970",
    "transaction_id": "8a89985a-4bbd-11e9-8a7c-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8a875cca-4bbd-11e9-a4cd-0cc47a172970",
    "transaction_id": "8a9005c8-4bbd-11e9-943f-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8a9a5190-4bbd-11e9-b6cf-0cc47a172970",
    "transaction_id": "8a9c768c-4bbd-11e9-8b49-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8a9a5190-4bbd-11e9-b6cf-0cc47a172970",
    "transaction_id": "8aa31dc0-4bbd-11e9-b38d-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8cf1801c-4bcc-11e9-8341-0cc47a172970",
    "transaction_id": "8cf35360-4bcc-11e9-b650-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8cf1801c-4bcc-11e9-8341-0cc47a172970",
    "transaction_id": "8cf8b7d8-4bcc-11e9-8cde-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8d39a834-4af9-11e9-bf1d-002590569245",
    "transaction_id": "8d3c1aba-4af9-11e9-972b-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "8d39a834-4af9-11e9-bf1d-002590569245",
    "transaction_id": "8d434ea2-4af9-11e9-8cba-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "8d45c7de-4bc3-11e9-84b9-0cc47a172970",
    "transaction_id": "8d47daba-4bc3-11e9-b5f0-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8d45c7de-4bc3-11e9-84b9-0cc47a172970",
    "transaction_id": "8d4f3b7a-4bc3-11e9-bbe4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8d862b06-4bc0-11e9-bb42-0cc47a172970",
    "transaction_id": "8d884c92-4bc0-11e9-a5f4-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8d862b06-4bc0-11e9-bb42-0cc47a172970",
    "transaction_id": "8d8e56f0-4bc0-11e9-b9ab-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8ddd82b4-4bbd-11e9-a0fc-0cc47a172970",
    "transaction_id": "8ddf4784-4bbd-11e9-b7ce-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8ddd82b4-4bbd-11e9-a0fc-0cc47a172970",
    "transaction_id": "8de45184-4bbd-11e9-a84e-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "8f464ef8-4b02-11e9-8f85-002590569245",
    "transaction_id": "8f4bd01c-4b02-11e9-ba6c-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "8f464ef8-4b02-11e9-8f85-002590569245",
    "transaction_id": "8f52cfde-4b02-11e9-80be-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "8fb15bfc-4bd0-11e9-8e44-0cc47a172970",
    "transaction_id": "8fb41fd6-4bd0-11e9-a88f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "8fb15bfc-4bd0-11e9-8e44-0cc47a172970",
    "transaction_id": "8fbc30b8-4bd0-11e9-9e2f-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "90471c78-4bdf-11e9-9728-0cc47a172970",
    "transaction_id": "904d6b46-4bdf-11e9-b64c-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "90471c78-4bdf-11e9-9728-0cc47a172970",
    "transaction_id": "905faf40-4bdf-11e9-8d55-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "90e64ab8-4bbd-11e9-99f1-0cc47a172970",
    "transaction_id": "90e867da-4bbd-11e9-9cb9-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "90e64ab8-4bbd-11e9-99f1-0cc47a172970",
    "transaction_id": "90edaab0-4bbd-11e9-9368-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "929638c2-4b05-11e9-86cd-002590569245",
    "transaction_id": "9298ab20-4b05-11e9-bfaf-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "935d45e0-4b03-11e9-bcc1-002590569245",
    "transaction_id": "935ff1be-4b03-11e9-830e-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "935d45e0-4b03-11e9-bcc1-002590569245",
    "transaction_id": "93668c7c-4b03-11e9-b07a-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "9448722c-4bcb-11e9-9e6b-0cc47a172970",
    "transaction_id": "9449e2ec-4bcb-11e9-a3af-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "9448722c-4bcb-11e9-9e6b-0cc47a172970",
    "transaction_id": "944eeea4-4bcb-11e9-898e-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "955a4c52-4bc7-11e9-8bea-0cc47a172970",
    "transaction_id": "955bfc32-4bc7-11e9-adf3-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "955a4c52-4bc7-11e9-8bea-0cc47a172970",
    "transaction_id": "95631940-4bc7-11e9-9d2d-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "95c4f3ce-4bc0-11e9-ab85-0cc47a172970",
    "transaction_id": "95c63bbc-4bc0-11e9-874f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "95c4f3ce-4bc0-11e9-ab85-0cc47a172970",
    "transaction_id": "95ccfee8-4bc0-11e9-8568-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "963e628e-4bd1-11e9-a44a-0cc47a172970",
    "transaction_id": "96401282-4bd1-11e9-92ea-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "9796e8bc-4bd7-11e9-a9cf-0cc47a172970",
    "transaction_id": "9799780c-4bd7-11e9-9349-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "9796e8bc-4bd7-11e9-a9cf-0cc47a172970",
    "transaction_id": "97a22600-4bd7-11e9-8335-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "980fc0aa-4bde-11e9-9c0c-002590ea2218",
    "transaction_id": "9811d4a8-4bde-11e9-b182-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "98744958-4bca-11e9-b3ae-002590ea2218",
    "transaction_id": "987648de-4bca-11e9-b552-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "98744958-4bca-11e9-b3ae-002590ea2218",
    "transaction_id": "987e60dc-4bca-11e9-9ce8-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "98b269a8-4b03-11e9-be0f-002590569245",
    "transaction_id": "98b451b4-4b03-11e9-b771-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "9952c090-4bd2-11e9-9f6d-0cc47a172970",
    "transaction_id": "99560c46-4bd2-11e9-9a28-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "9a8dc544-4bd8-11e9-ae0c-0cc47a172970",
    "transaction_id": "9a8fb5fc-4bd8-11e9-b710-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "9a8dc544-4bd8-11e9-ae0c-0cc47a172970",
    "transaction_id": "9a983f9c-4bd8-11e9-9e2d-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "9c42b878-4bd7-11e9-a681-002590ea2218",
    "transaction_id": "9c45a060-4bd7-11e9-a134-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "9c42b878-4bd7-11e9-a681-002590ea2218",
    "transaction_id": "9c4f425a-4bd7-11e9-88f7-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "9c4f3836-4bba-11e9-bd12-0cc47a172970",
    "transaction_id": "9c4fe010-4bba-11e9-be65-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "9c42b878-4bd7-11e9-a681-002590ea2218",
    "transaction_id": "9c60c868-4bd7-11e9-a4c3-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "9cd2284e-4bd4-11e9-bd7d-0cc47a172970",
    "transaction_id": "9cd43d0a-4bd4-11e9-ac88-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "9cd2284e-4bd4-11e9-bd7d-0cc47a172970",
    "transaction_id": "9cdb941a-4bd4-11e9-82e8-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "9cd2284e-4bd4-11e9-bd7d-0cc47a172970",
    "transaction_id": "9cdee854-4bd4-11e9-9795-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "9de6405c-4bdf-11e9-95b9-002590ea2218",
    "transaction_id": "9de82b24-4bdf-11e9-a46e-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "9de6405c-4bdf-11e9-95b9-002590ea2218",
    "transaction_id": "9df05e02-4bdf-11e9-b0d9-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "9de6405c-4bdf-11e9-95b9-002590ea2218",
    "transaction_id": "9df6a87a-4bdf-11e9-8c55-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "9edbaaf8-4bba-11e9-968c-0cc47a172970",
    "transaction_id": "9edcdd56-4bba-11e9-8016-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "a233278c-4bd1-11e9-bf75-002590ea2218",
    "transaction_id": "a2352758-4bd1-11e9-b276-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "a233278c-4bd1-11e9-bf75-002590ea2218",
    "transaction_id": "a23d95e6-4bd1-11e9-aa22-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "a2925d48-4bd5-11e9-bda0-0cc47a172970",
    "transaction_id": "a298b81e-4bd5-11e9-911f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "a2925d48-4bd5-11e9-bda0-0cc47a172970",
    "transaction_id": "a2a2ca34-4bd5-11e9-9fbb-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "a5a44aea-4bc2-11e9-bb54-0cc47a172970",
    "transaction_id": "a5a78804-4bc2-11e9-b79b-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "a5a44aea-4bc2-11e9-bb54-0cc47a172970",
    "transaction_id": "a5af41c0-4bc2-11e9-b88c-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "a9c31e3a-4afa-11e9-8df5-002590569245",
    "transaction_id": "a9c5a880-4afa-11e9-b5d4-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "a9c31e3a-4afa-11e9-8df5-002590569245",
    "transaction_id": "a9ccd088-4afa-11e9-b52d-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "aa3a2e4a-4bd5-11e9-8b69-0cc47a172970",
    "transaction_id": "aa3c7952-4bd5-11e9-a933-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "aa459bf6-4bce-11e9-9441-0cc47a172970",
    "transaction_id": "aa489766-4bce-11e9-b9fe-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "aa459bf6-4bce-11e9-9441-0cc47a172970",
    "transaction_id": "aa5001fe-4bce-11e9-ac28-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "ac9bfc7c-4bda-11e9-a0b3-002590ea2218",
    "transaction_id": "ac9ff43a-4bda-11e9-94f6-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "ac9bfc7c-4bda-11e9-a0b3-002590ea2218",
    "transaction_id": "aca6e4d4-4bda-11e9-a47b-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "acbd21de-4bdc-11e9-b953-0cc47a172970",
    "transaction_id": "acc3e500-4bdc-11e9-bb20-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "ad6344d0-4bda-11e9-b7f3-002590ea2218",
    "transaction_id": "ad661e6c-4bda-11e9-aef3-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "ad6344d0-4bda-11e9-b7f3-002590ea2218",
    "transaction_id": "ad6bb78c-4bda-11e9-b597-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "af134be4-4af5-11e9-b0ee-002590569245",
    "transaction_id": "af18d85c-4af5-11e9-88b0-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "af134be4-4af5-11e9-b0ee-002590569245",
    "transaction_id": "af2016f8-4af5-11e9-8246-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "b05af202-4bba-11e9-a96c-0cc47a172970",
    "transaction_id": "b05cb740-4bba-11e9-a3a5-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "b1441908-4bda-11e9-9f63-002590ea2218",
    "transaction_id": "b146b532-4bda-11e9-a450-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "b1441908-4bda-11e9-9f63-002590ea2218",
    "transaction_id": "b14cfd66-4bda-11e9-877b-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "b17a0a90-4b03-11e9-bca6-002590569245",
    "transaction_id": "b17c8edc-4b03-11e9-9fa1-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "b17a0a90-4b03-11e9-bca6-002590569245",
    "transaction_id": "b1841c7e-4b03-11e9-8b14-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "b1eb9e74-4bd2-11e9-9d2c-0cc47a172970",
    "transaction_id": "b1edf34a-4bd2-11e9-80fb-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "b1eb9e74-4bd2-11e9-9d2c-0cc47a172970",
    "transaction_id": "b1f5f8f6-4bd2-11e9-b319-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "b1eb9e74-4bd2-11e9-9d2c-0cc47a172970",
    "transaction_id": "b1fd849a-4bd2-11e9-9c05-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "b342a07a-4bbd-11e9-8ba9-0cc47a172970",
    "transaction_id": "b3445db6-4bbd-11e9-b745-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "b342a07a-4bbd-11e9-8ba9-0cc47a172970",
    "transaction_id": "b354351a-4bbd-11e9-946c-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "b3a98eda-4bda-11e9-9ee3-002590ea2218",
    "transaction_id": "b3aca03e-4bda-11e9-a749-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "b3a98eda-4bda-11e9-9ee3-002590ea2218",
    "transaction_id": "b3b23f6c-4bda-11e9-96ec-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "b3d4a674-4bda-11e9-94bd-002590ea2218",
    "transaction_id": "b3d76e04-4bda-11e9-878d-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "b3d4a674-4bda-11e9-94bd-002590ea2218",
    "transaction_id": "b3dcaa54-4bda-11e9-b10e-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "b6ba7b54-4afc-11e9-9853-002590569245",
    "transaction_id": "b6bc5f46-4afc-11e9-999a-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "b6ce09b0-4b03-11e9-8f43-002590569245",
    "transaction_id": "b6cfe9b0-4b03-11e9-ae8e-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "b6ce09b0-4b03-11e9-8f43-002590569245",
    "transaction_id": "b6d6cfe6-4b03-11e9-87d7-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "b74c2ba6-4bda-11e9-8601-002590ea2218",
    "transaction_id": "b74e94d6-4bda-11e9-a66c-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "b74c2ba6-4bda-11e9-8601-002590ea2218",
    "transaction_id": "b756726e-4bda-11e9-a66d-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "bb16e0e6-4aea-11e9-a22b-002590569245",
    "transaction_id": "bb18e38c-4aea-11e9-a9eb-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "bb16e0e6-4aea-11e9-a22b-002590569245",
    "transaction_id": "bb245582-4aea-11e9-b6c4-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "bb16e0e6-4aea-11e9-a22b-002590569245",
    "transaction_id": "bb28bfaa-4aea-11e9-8b6e-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "bbbe1168-4bd0-11e9-963f-0cc47a172970",
    "transaction_id": "bbc0859c-4bd0-11e9-b0cb-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "bbbe1168-4bd0-11e9-963f-0cc47a172970",
    "transaction_id": "bbc790ee-4bd0-11e9-9060-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "bd2254ce-4bdf-11e9-84af-0cc47a172970",
    "transaction_id": "bd24472a-4bdf-11e9-a52f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "bd2254ce-4bdf-11e9-84af-0cc47a172970",
    "transaction_id": "bd2d398e-4bdf-11e9-b4ef-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "be799884-4bba-11e9-b387-0cc47a172970",
    "transaction_id": "be7ac150-4bba-11e9-a75a-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "be799884-4bba-11e9-b387-0cc47a172970",
    "transaction_id": "be80b074-4bba-11e9-b000-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "bf1c294c-4bc8-11e9-a841-002590ea2218",
    "transaction_id": "bf1e7d78-4bc8-11e9-aca1-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "c1d4adbc-4bd7-11e9-a111-0cc47a172970",
    "transaction_id": "c1d69de8-4bd7-11e9-95f0-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "c1d4adbc-4bd7-11e9-a111-0cc47a172970",
    "transaction_id": "c1de0e66-4bd7-11e9-8ad2-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "c545ca62-4bc8-11e9-8cb3-0cc47a172970",
    "transaction_id": "c5480ce6-4bc8-11e9-ac6f-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "c545ca62-4bc8-11e9-8cb3-0cc47a172970",
    "transaction_id": "c54df976-4bc8-11e9-9b3a-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "c5d921de-4bbb-11e9-8e4e-0cc47a172970",
    "transaction_id": "c5dde278-4bbb-11e9-907c-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "c5d921de-4bbb-11e9-8e4e-0cc47a172970",
    "transaction_id": "c5e4fc3e-4bbb-11e9-9ff2-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "c6a377fc-4bbd-11e9-8c6e-0cc47a172970",
    "transaction_id": "c6a5e172-4bbd-11e9-848c-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "c6a377fc-4bbd-11e9-8c6e-0cc47a172970",
    "transaction_id": "c6acb9f2-4bbd-11e9-8792-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "c7cbcf2a-4bd7-11e9-98a5-002590ea2218",
    "transaction_id": "c7ce1154-4bd7-11e9-a7d8-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "c7cbcf2a-4bd7-11e9-98a5-002590ea2218",
    "transaction_id": "c7d4d43a-4bd7-11e9-ac3a-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "cc82b7f6-4aea-11e9-a28f-002590569245",
    "transaction_id": "cc84d0fe-4aea-11e9-9f61-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "cc82b7f6-4aea-11e9-a28f-002590569245",
    "transaction_id": "cc92bfa2-4aea-11e9-ba78-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "cda04664-4b1a-11e9-af40-002590569245",
    "transaction_id": "cda1f4d2-4b1a-11e9-b379-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "cdc8c5a6-4bbc-11e9-a575-002590ea2218",
    "transaction_id": "cdcb5c08-4bbc-11e9-8c4f-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "d185644a-4bd2-11e9-bde7-0cc47a172970",
    "transaction_id": "d18791de-4bd2-11e9-a9bd-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "d300dcfe-4bba-11e9-8ac0-0cc47a172970",
    "transaction_id": "d3026c86-4bba-11e9-b73e-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "d300dcfe-4bba-11e9-8ac0-0cc47a172970",
    "transaction_id": "d309a2ee-4bba-11e9-87e4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "d41902a8-4af5-11e9-989d-002590569245",
    "transaction_id": "d41c9a62-4af5-11e9-b1ff-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "d41902a8-4af5-11e9-989d-002590569245",
    "transaction_id": "d42407c0-4af5-11e9-81bb-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "da41dcc8-4bd0-11e9-b652-0cc47a172970",
    "transaction_id": "da43d29e-4bd0-11e9-9359-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "da41dcc8-4bd0-11e9-b652-0cc47a172970",
    "transaction_id": "da4aeaa2-4bd0-11e9-9321-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "dad9f8aa-4bd5-11e9-a93b-0cc47a172970",
    "transaction_id": "daddec94-4bd5-11e9-abac-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "dcf63980-4b05-11e9-af97-002590569245",
    "transaction_id": "dcf81872-4b05-11e9-a311-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "dd3d3f16-4bd1-11e9-a438-0cc47a172970",
    "transaction_id": "dd3f8410-4bd1-11e9-b130-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "dd3d3f16-4bd1-11e9-a438-0cc47a172970",
    "transaction_id": "dd48c70a-4bd1-11e9-8d3d-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "e29a3f76-4b05-11e9-8fb8-002590569245",
    "transaction_id": "e29c8858-4b05-11e9-85f8-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "e5120e82-4bdc-11e9-9352-0cc47a172970",
    "transaction_id": "e513f6d4-4bdc-11e9-b071-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "e5120e82-4bdc-11e9-9352-0cc47a172970",
    "transaction_id": "e51b6a2c-4bdc-11e9-8ce1-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "e61e427e-4af5-11e9-bc67-002590569245",
    "transaction_id": "e620c6d4-4af5-11e9-a3f1-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "e61e427e-4af5-11e9-bc67-002590569245",
    "transaction_id": "e6286074-4af5-11e9-bd33-002590569245",
    "transaction_type": 8
  },
  {
    "operation_id": "e6869568-4bd1-11e9-95b8-0cc47a172970",
    "transaction_id": "e689295e-4bd1-11e9-9642-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "e7061a72-4bd1-11e9-b581-0cc47a172970",
    "transaction_id": "e707a16c-4bd1-11e9-b510-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "e7061a72-4bd1-11e9-b581-0cc47a172970",
    "transaction_id": "e70d7740-4bd1-11e9-9afc-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "e8889dba-4bdc-11e9-b465-0cc47a172970",
    "transaction_id": "e889e8c8-4bdc-11e9-8cc7-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "e8889dba-4bdc-11e9-b465-0cc47a172970",
    "transaction_id": "e89140be-4bdc-11e9-b0b4-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "e8889dba-4bdc-11e9-b465-0cc47a172970",
    "transaction_id": "e89702ce-4bdc-11e9-ba71-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "e922de66-4bd2-11e9-9ce7-0cc47a172970",
    "transaction_id": "e9251aa0-4bd2-11e9-96bf-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "ed4d733a-4bd1-11e9-84c5-0cc47a172970",
    "transaction_id": "ed4f78f6-4bd1-11e9-874c-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "ed76ebaa-4bc9-11e9-8cd0-002590ea2218",
    "transaction_id": "ed7d9ab8-4bc9-11e9-83da-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "ed76ebaa-4bc9-11e9-8cd0-002590ea2218",
    "transaction_id": "ed86352e-4bc9-11e9-826c-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "eeacec1a-4bd1-11e9-8efb-0cc47a172970",
    "transaction_id": "eeaeac8a-4bd1-11e9-a517-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "eeacec1a-4bd1-11e9-8efb-0cc47a172970",
    "transaction_id": "eeb42b24-4bd1-11e9-89e3-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "eec85430-4bce-11e9-b341-0cc47a172970",
    "transaction_id": "eecad0d4-4bce-11e9-92f8-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "eec85430-4bce-11e9-b341-0cc47a172970",
    "transaction_id": "eed26d9e-4bce-11e9-9dfb-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "f0d81626-4b05-11e9-9512-002590569245",
    "transaction_id": "f0daa29c-4b05-11e9-95d5-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "f1a74c1e-4bbb-11e9-8bfa-002590ea2218",
    "transaction_id": "f1a94280-4bbb-11e9-a6c6-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "f1a74c1e-4bbb-11e9-8bfa-002590ea2218",
    "transaction_id": "f1b1c2c0-4bbb-11e9-9b36-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "f341789c-4bcf-11e9-a30c-0cc47a172970",
    "transaction_id": "f3439226-4bcf-11e9-8244-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "f341789c-4bcf-11e9-a30c-0cc47a172970",
    "transaction_id": "f34a719a-4bcf-11e9-8783-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "f45dfa5e-4bb9-11e9-b322-0cc47a172970",
    "transaction_id": "f46416a0-4bb9-11e9-918a-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "f45dfa5e-4bb9-11e9-b322-0cc47a172970",
    "transaction_id": "f474e4d0-4bb9-11e9-ade8-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "f526c42c-4bcb-11e9-8b3b-0cc47a172970",
    "transaction_id": "f5299eb8-4bcb-11e9-acfc-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "f526c42c-4bcb-11e9-8b3b-0cc47a172970",
    "transaction_id": "f53123fe-4bcb-11e9-a7b7-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "f5350a44-4b05-11e9-a79b-002590569245",
    "transaction_id": "f5378c10-4b05-11e9-8ecf-002590569245",
    "transaction_type": 3
  },
  {
    "operation_id": "f59b0d2c-4bd1-11e9-94b5-002590ea2218",
    "transaction_id": "f59d35fc-4bd1-11e9-a06c-002590ea2218",
    "transaction_type": 3
  },
  {
    "operation_id": "f59b0d2c-4bd1-11e9-94b5-002590ea2218",
    "transaction_id": "f5a44a40-4bd1-11e9-b142-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "f59b0d2c-4bd1-11e9-94b5-002590ea2218",
    "transaction_id": "f5a89e42-4bd1-11e9-a386-002590ea2218",
    "transaction_type": 8
  },
  {
    "operation_id": "fa21817e-4bc6-11e9-8989-0cc47a172970",
    "transaction_id": "fa23b494-4bc6-11e9-bb4a-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "fa21817e-4bc6-11e9-8989-0cc47a172970",
    "transaction_id": "fa2b9772-4bc6-11e9-b304-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "fa37ee04-4bd1-11e9-93ab-0cc47a172970",
    "transaction_id": "fa39ba7c-4bd1-11e9-a483-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "fa37ee04-4bd1-11e9-93ab-0cc47a172970",
    "transaction_id": "fa3f3d9e-4bd1-11e9-8792-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "fafa8b90-4bc1-11e9-a5eb-0cc47a172970",
    "transaction_id": "fafd8db8-4bc1-11e9-a18c-0cc47a172970",
    "transaction_type": 3
  },
  {
    "operation_id": "fafa8b90-4bc1-11e9-a5eb-0cc47a172970",
    "transaction_id": "fb06d0e4-4bc1-11e9-b49c-0cc47a172970",
    "transaction_type": 8
  },
  {
    "operation_id": "fe062e7a-4bd5-11e9-b96c-0cc47a172970",
    "transaction_id": "fe07bc54-4bd5-11e9-bc09-0cc47a172970",
    "transaction_type": 3
  }
]



# product_cell = re.compile(r'^(\d*)(?:\-(\d*))?$')

# def decode_product(cell):
#     match = product_cell.search(cell.strip())
#     if match is None: 
#         return (None, None)
#     return match.groups()[0:2]

# print(decode_product('12-201'))
# print(decode_product('12'))
# print(decode_product('12-201-2000'))

# print(decode_product('12-201 '))
# print(decode_product(' 12 '))
# print(decode_product('12-201-2000   '))

print(_.group_by(data, 'operation_id'))