'use strict';

var app = angular.module('myApp', ['ui.select', 'ngSanitize', 'chart.js']);
app.config(['uiSelectConfig', 'ChartJsProvider', function (uiSelectConfig, ChartJsProvider) {
    // uiSelectConfig.theme = 'select2';
    uiSelectConfig.theme = 'selectize';
    // ChartJsProvider.setOptions({
    //     chartColors: ['#FF5252', '#FF8A80'],
    //     responsive: false
    // });
    // // Configure all line charts
    // ChartJsProvider.setOptions('line', {
    //     showLines: false
    // });

}]);
app.controller('myCtrl', function ($scope, $http, $timeout) {

    $scope.selecteItem = {};
    $scope.selectedProduct = {};
    $scope.selectedStatusArray = [];
    $scope.selectedDistricts = [];
    $scope.labels = [];
    $scope.data = [
        []
    ];
    $scope.showStockStatusChartLoader=false;


     //line chart
    $scope.showStockTrendChartLoader=false;
    $scope.lineChartData=[[]];
    $scope.lineChartData = [
    [65, 59, 80, 81, 56, 55, 40],
    [28, 48, 40, 19, 86, 27, 90]
  ];

    $scope.lineChartLabels=[];
    $scope.selectedTrendProduct=[];




     $http({
        method: 'GET',
        url: '/lookups'
    }).then(function successCallback(response) {

        console.log(response);
       $scope.itemArray = flattenGeoTree(response.data.geoTree);
         $scope.productArray = response.data.allProducts.products;
        $scope.statusArray = response.data.allProducts.status;
    }, function errorCallback(response) {

        console.log(response);
    });

    // $http({
    //     method: 'GET',
    //     url: '/geo-tree-lookup'
    // }).then(function successCallback(response) {
    //     console.log(response);
    //     $scope.itemArray = flattenGeoTree(response.data.geoTree);
    // }, function errorCallback(response) {
    //
    //     console.log(response);
    // });


    // $http({
    //     method: 'GET',
    //     url: '/products-lookup'
    // }).then(function successCallback(response) {
    //     console.log(response);
    //
    //     $scope.productArray = response.data.products;
    //     $scope.statusArray = response.data.status;
    //
    // }, function errorCallback(response) {
    //
    //     console.log(response);
    // });

    function flattenGeoTree(geoTree) {
        let flatGeo = [];
        generateGeoZones(geoTree, flatGeo);
        return flatGeo;
    }

    function generateGeoZones(node, flatGeoList) {
        flatGeoList.push(
            {
                id: node.id,
                name: node.name,
                parentId: node.parentId,
                level:node.level

            }
        );
        angular.forEach(node.children, function (childNode, key) {
            generateGeoZones(childNode, flatGeoList);
        });
    }


    // $scope.series = ['Series A'];
    // $scope.colors = [{
    //     fillColor: 'rgba(47, 132, 71, 0.8)',
    //     strokeColor: 'rgba(47, 132, 71, 0.8)',
    //     highlightFill: 'rgba(47, 132, 71, 0.8)',
    //     highlightStroke: 'rgba(47, 132, 71, 0.8)'
    // }];

    $scope.onClick = function (points, evt) {
        console.log(points, evt);
    };

    // Simulate async data update
    // $timeout(function () {
    //     $scope.data = [
    //         [28, 48, 40, 19, 86]
    //     ];
    // }, 3000);


    $scope.onGeoZoneSelected = function ($item, $model) {
        let districts = generateDistrictIds($item);
        if (_.has(districts, 'parentId')) {
            districts = [districts];
        } else {
            districts = _.flatten(districts);
        }
        $scope.selectedDistricts = districts;
        $scope.selecteItem = $item;
        getStockStatusData()
    }

     $scope.onGeoZoneTrendSelected = function ($item, $model) {
        let districts = generateDistrictIds($item);
        if (_.has(districts, 'parentId')) {
            districts = [districts];
        } else {
            districts = _.flatten(districts);
        }
        // $scope.selectedDistricts = districts;
        // $scope.selecteItem = $item;
        // getStockStatusData()
    }

    $scope.onProductSelected = function ($item, $model) {
        $scope.selectedProduct = $item;
        getStockStatusData()

    }

    $scope.onProductSelectedTrend = function ($item, $model) {
        // $scope.selectedProduct = $item;
        // getStockStatusData()

    }

    $scope.onStatusSelected = function ($item, $model) {

        //TODO :: check if exist before adding;
        $scope.selectedStatus = $item;
        $scope.selectedStatusArray.push($item);
        getStockStatusData()
    }

    $scope.onStatusRemoved = function ($item, $model) {
        //TODO :: check if exist before removing;
        let index = $scope.selectedStatusArray.indexOf($item);
        if (index > -1) {
            $scope.selectedStatusArray.splice(index, 1);
            getStockStatusData();
        }

    }


    function generateDistrictIds(selectedZone) {

        // let districtIds = _.filter($scope.itemArray, function (zone) {
        //     return selectedZone.id == zone.parentId;
        // });
        // if (districtIds.length !== 0) {
        //     return districtIds;
        // }
        // return selectedZone;
        return recurseGenerateDistrictIds(selectedZone);

    }

    function recurseGenerateDistrictIds(selectedZone) {

        let districtIds = _.filter($scope.itemArray, function (zone) {
            return selectedZone.id == zone.parentId;
        })

        let others = [];
        if (districtIds.length !== 0) {

            _.each(districtIds, function (param) {
                others.push(
                    recurseGenerateDistrictIds(param)
                )
            });
            return others;
        }
        return selectedZone;
    }


    function getStockStatusData() {
        if (_.isEmpty($scope.selectedDistricts) || _.isEmpty($scope.selectedProduct) || _.isEmpty($scope.selectedStatusArray)) {
            console.log('hide graph and how text');
            $scope.labels = [];
            $scope.data = [
                []
            ];
            return;
        }
        $scope.showStockStatusChartLoader=true;
        let selectedDistrictIds = _.pluck($scope.selectedDistricts, 'id');
        let productId = $scope.selectedProduct.id;
        let selectedStatusIds = _.pluck($scope.selectedStatusArray, 'id');
        $http({
            url: '/get_stock_stauts',
            method: "GET",
            params: {productId: productId, districtIds: selectedDistrictIds, statusIds: selectedStatusIds}
        }).then(function successCallback(response) {
            renderStockStatusChart(response)
        }, function errorCallback(response) {

            console.log(response);
        });


    }

    function renderStockStatusChart(response) {
        let prepareLabel = [];
        let prepareData = [];
        let dataInPrepare = [];
        let prepareColor=[];
        angular.forEach(response.data.results, function (st) {
            prepareLabel.push(st.name);
            dataInPrepare.push(st.count);
            prepareColor.push(st.color);
        });
        prepareData.push(dataInPrepare);
        $scope.labels = prepareLabel;
        $scope.data = prepareData;
        $scope.colors=prepareColor;
        $scope.showStockStatusChartLoader=false;
    }


    //end of line
});
