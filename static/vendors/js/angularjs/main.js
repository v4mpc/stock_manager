var app = angular.module('myApp', ['angularFileUpload', 'ngSanitize']);
app.controller('myCtrl', function ($scope, $http, FileUploader, $timeout) {
    $scope.uploadSuccess = false;
    $scope.documentToDownload = '';
    $scope.uploadErrorMessage = [];
    $scope.docs = [];
    let messageTimout = 1000 * 20; //seconds
    let value = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    $scope.uploader = new FileUploader({
            url: '/upload_doc/',
            queueLimit: 1,
            alias: 'file',
            removeAfterUpload: true,

        }
    );

    function reset_file_input() {
        angular.forEach(
            angular.element("input[type='file']"),
            function (inputElem) {
                console.log(inputElem);
                angular.element(inputElem).val(null);
            });
    }

    $http({
        method: 'GET',
        url: '/upload_docs_lookup'
    }).then(function successCallback(response) {
        angular.forEach(response.data.docs, function (value, key) {
            $scope.docs.push({
                'value': value,
                'name': value
            });
        })
    }, function errorCallback(response) {
        console.log(response);
    });

    $scope.uploader.onCompleteAll = function () {
        reset_file_input();
    };


    $scope.uploader.onSuccessItem = function (item, response, status, headers) {
        $scope.uploadSuccess = true;
        $timeout(function () {
            $scope.uploadSuccess = false;
        }, messageTimout)
    }


    $scope.uploader.onErrorItem = function (item, response, status, headers) {
        console.log(response);
        $scope.uploadErrorMessage = [];
        var _code = response.error.code
        var _message = response.error.message
        if (_code == 'CONTENT_ERROR') {
            angular.forEach(response.error.message, function (value, key) {
                $scope.uploadErrorMessage.push(
                    `<b>${value[4]}</b>: ${value[3]} on <b>Column</b> :${value[2]} at <b>Row</b>: ${value[1]}`
                )
            });

        } else if (_code == 'EXTENSION_ERROR') {
            $scope.uploadErrorMessage.push(response.error.message);
        }
        else if (_code == 'FILE_TYPE_ERROR') {
            $scope.uploadErrorMessage.push(response.error.message);
        } else if (_code == 'FORM_ERROR') {
            console.log(_message);
            var formKeys = Object.keys(_message);
            angular.forEach(formKeys,function (value,key) {
                $scope.uploadErrorMessage.push(
                    `${value} : ${_message[value][0]}`
                )
            })
        } else {
            console.log(response)
            $scope.uploadErrorMessage.push('Unknown error Contact Admin')
        }
        $timeout(function () {
            $scope.uploadErrorMessage = [];
        }, messageTimout);


    }
    $scope.uploader.onTimeoutItem = function (fileItem) {
        console.info('onTimeoutItem', fileItem);
    };


    $scope.uploader.onBeforeUploadItem = function (item) {
        item.formData = [{
            'csrfmiddlewaretoken': value,
            'uploaded_file_type': $scope.selectedDoc.value,
        }];


    }

    $scope.onDocumentChanged = function () {
        if (!$scope.selectedDoc) {
            $scope.uploader.clearQueue();
            reset_file_input();

        } else {
            $scope.uploader.formData = [{
                'csrfmiddlewaretoken': value,
                'uploaded_file_type': $scope.selectedDoc.value
            }]
        }
    }

});
app.filter('trustAsHtml', ['$sce', function ($sce) {
    return $sce.trustAsHtml;
}]);
