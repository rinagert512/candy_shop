from .logger import log
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourierSerializer
from .models import *
import datetime
from dateutil import parser


class CouriersView(APIView):
    def post(self, request):
        try:
            objects = request.data['data']
            validated = []
            error = []

            for json_obj in objects:
                try:
                    instance = Courier(
                        courier_id=json_obj['courier_id'],
                        courier_type=json_obj['courier_type'],
                        regions=json_obj['regions'],
                        working_hours=json_obj['working_hours']
                    )
                    instance.full_clean()
                    validated.append(instance)
                except Exception as e:
                    log(e)
                    error.append({
                        'id': json_obj['courier_id']
                    })

            if len(error):
                return Response(
                    {
                        "validation_error": {
                            "couriers": error
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            successful = []
            for item in validated:
                item.save()
                successful.append({
                    'id': item.courier_id
                })

            return Response(
                {
                    "couriers": successful
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            log(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CourierView(APIView):
    def patch(self, request, pk):
        try:
            courier = Courier.objects.filter(courier_id=pk).first()

            allowed_fields = [
                'courier_type',
                'regions',
                'working_hours'
            ]

            for key in request.data.keys():
                if not (key in allowed_fields):
                    raise Exception("Illegal field")

            for key in request.data.keys():
                setattr(courier, key, request.data[key])

            courier.full_clean()
            courier.save()

            serializer = CourierSerializer(courier)

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            log(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk):
        try:
            courier = Courier.objects.filter(courier_id=pk).first()
            response = CourierSerializer(courier).data

            completed_orders = Order.objects.filter(courier=courier).exclude(complete_time=None)
            if not len(completed_orders):
                return Response(response, status=status.HTTP_200_OK)

            td = []
            for region in courier.regions:
                region_orders = list(completed_orders.filter(region=region))
                region_orders = sorted(region_orders, key=lambda x: x.complete_time)
                if not len(region_orders):
                    td.append(3600)
                else:
                    times = []
                    for i in range(len(region_orders)):
                        if i == 0:
                            delta = region_orders[i].complete_time - region_orders[i].assign_time
                            times.append(delta.total_seconds())
                        else:
                            delta = region_orders[i].complete_time - region_orders[i - 1].assign_time
                            times.append(delta.total_seconds())
                    td.append(sum(times) / len(times))

            t = min(td)
            rating = (60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5
            coefficients = {
                'foot': 2,
                'bike': 5,
                'car': 9
            }
            c = coefficients[courier.courier_type]
            earnings = 500 * c * len(completed_orders)

            response['rating'] = rating
            response['earnings'] = earnings
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            log(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrdersView(APIView):
    def post(self, request):
        try:
            orders = request.data['data']
            validated = []
            error = []

            for json_obj in orders:
                try:
                    instance = Order(
                        order_id=json_obj['order_id'],
                        weight=json_obj['weight'],
                        region=json_obj['region'],
                        delivery_hours=json_obj['delivery_hours']
                    )
                    instance.full_clean()
                    validated.append(instance)
                except Exception as e:
                    log(e)
                    error.append({
                        'id': json_obj['order_id']
                    })

            if len(error):
                return Response(
                    {
                        "validation_error": {
                            "orders": error
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            successful = []
            for item in validated:
                item.save()
                successful.append({
                    'id': item.order_id
                })

            return Response(
                {
                    "orders": successful
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            log(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrdersAssignView(APIView):
    def post(self, request):
        try:
            courier_id = request.data['courier_id']
            courier = Courier.objects.filter(courier_id=courier_id).first()

            if not courier:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            capacities = {
                'foot': 10,
                'bike': 15,
                'car': 50
            }
            lifting_capacity = capacities[courier.courier_type]
            orders = list(Order.objects.all())
            suitable = []

            for order in orders:
                if order.weight > lifting_capacity:
                    continue
                if not (order.region in courier.regions):
                    continue
                if order.complete_time:
                    continue

                in_time_range = False
                for time_range in courier.working_hours:
                    get_time = lambda x: datetime.time(
                        hour=int(x.split(':')[0]),
                        minute=int(x.split(':')[1])
                    )

                    start_courier_time = get_time(time_range.split('-')[0])
                    end_courier_time = get_time(time_range.split('-')[1])

                    for order_time_range in order.delivery_hours:
                        start = get_time(order_time_range.split('-')[0])
                        end = get_time(order_time_range.split('-')[1])
                        if start >= start_courier_time and end <= end_courier_time:
                            in_time_range = True
                            break

                    if in_time_range:
                        break

                if in_time_range:
                    suitable.append(order)

            assign_time = datetime.datetime.now()
            ret_list = []
            for order in suitable:
                order.courier = courier
                order.assign_time = assign_time
                order.save()
                ret_list.append({
                    'id': order.order_id
                })

            if len(suitable):
                return Response(
                    {
                        'orders': ret_list,
                        'assign_time': assign_time
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "orders": []
                    },
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            log(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class OrdersCompleteView(APIView):
    def post(self, request):
        try:
            order_id = request.data['order_id']
            courier_id = request.data['courier_id']
            complete_time = parser.parse(request.data['complete_time'])

            order = Order.objects.filter(order_id=order_id).first()
            if order.courier.courier_id != courier_id:
                raise Exception("Incorrect completion")
            order.complete_time = complete_time
            order.save()

            return Response(
                {
                    'order_id': order_id,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            log(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
