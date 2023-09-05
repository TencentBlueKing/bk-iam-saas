<!-- 2023-09-05 -->
# V1.10.13 Version Update Log

### New Features
* Added "not available for application" attribute setting to user groups

### Optimization Updates
* Synchronized the latest message specification and searchSelect specification across all platforms
* Users can now exit multiple user groups at once
* User group permission renewal page now displays description, administrator, and management space data
* Added member addition, member copying, and organizational structure functions to user groups
* Added search function to "My Permissions" page
* Removed query type filter from resource permission management, default query type is now instance permission

### Bug Fixes
* Fixed issue where clicking on renewal email link for Blue Shield project administrators resulted in blank webpage content
* Fixed issue where user group member renewal effective time stamp calculation was incorrect
* Fixed issue where Blue Shield permission transfer check for "disabled" was incorrect, added pagination to user group permission transfer and administrator transfer
* Fixed issue where modifying project name still resulted in timeout
* Fixed issue where user application for multiple groups resulted in error due to long title.

---

<!-- 2023-07-31 -->
# V1.10.12 ChangeLog

### New Features
* Custom permissions can be configured to allow multi-level administrator approval.
* Batch unlimited permissions have been added to user group creation, cloning, and permission addition.
* Batch copying of users and organization members has been added to user group management.

### Bug Fixes
Fixed an issue where clicking on "synchronize" in the user module->user type would result in a third-party interface exception.

---

<!-- 2023-07-26 -->
# V1.10.11 ChangeLog

### New Features
* Switching ESB interface login, supporting ESB authentication for application permissions.

---

<!-- 2023-07-17 -->
# V1.10.10 ChangeLog

### New Features
* Add department display to user group member list
* Add permission details to expired permission list
* Allow optional selection for aggregated operations
* Allow level 1 administrators to directly access level 2 administrators

---

<!-- 2023-07-07 -->
# V1.10.9 ChangeLog

### Bug Fixes
* Fixed the issue that the dependency operation was not synchronizing data when adding attribute conditions for user group permissions.
* Fixed the issue that the system administrator member editing was abnormal, and the input box of the system administrator member was abnormal.
* Added the requirement to add or remove all operation instances under a single system for "My Permissions".
* Adjusted the layout of the module for deleting and viewing user group permissions.

---

<!-- 2023-07-05 -->
# V1.10.8 ChangeLog

### Bug Fixes
* Fixing front-end internationalization issues

---

<!-- 2023-06-27 -->
# V1.10.7 ChangeLog

### New Features
* When deleting an instance with a custom permission, delete the instance that is dependent on the permission at the same time

### Bug Fixes
* ITSM bill of lading form field internationalization
* Language switching is set to BK_DOMAIN
* Hierarchical administrator synchronization permission user group name internationalization

---

<!-- 2023-06-21 -->
# V1.10.6 ChangeLog

### Bug Fixes
* Fixed the issue where the default workflow for the graded administrator was empty
* Fixed the issue with the audit log record table create name

---

<!-- 2023-06-07 -->
# V1.10.5 ChangeLog

### New Features
* Applying for user group permissions can be done by operating and searching user groups in the instances

### Optimization Updates
* Optimize the associated permission deletion logic

---

<!-- 2023-06-02 -->
# V1.10.4 ChangeLog

### New Features
* Added BCS automatic initialization of administrator user group, making it easier for administrators to set up the system.

### Bug Fixes
* Fixed a bug in the user list query list to improve normal system operation efficiency.
* Added max request number parameter for gunicorn to optimize system performance.

---

<!-- 2023-05-29 -->
# V1.10.3 ChangeLog

### Optimization Updates
* Optimize the method of creating dynamic fields in permission application approval form

---

<!-- 2023-05-25 -->
# V1.10.2 ChangeLog

### Optimization Updates
* Optimize the bkci permission migration function

---

<!-- 2023-05-18 -->
# V1.10.1 ChangeLog

### Bug Fixes
* The open api creation permission application form increases the expiration time
* Fix the unprocessed permission removal when submitting a custom permission application

---

<!-- 2023-05-10 -->
# V1.10.0 ChangeLog

### New Features
* Support secondary management space feature

---

<!-- 2023-03-28 -->
# V1.9.10 ChangeLog

### New Features
* Add temporary permission switch
* Modify the maximum number of tiered administrators that can be created in the api to 500

---

<!-- 2023-02-20 -->
# V1.9.9 ChangeLog

### Bug Fixes
* Management api user group authorization is not associated with resource instance conversion bug

---

<!-- 2023-01-31 -->
# V1.9.8 ChangeLog

### New Features
* Initialize rating administrator update custom action

### Bug Fixes
* Repair the healthz interface to actively close the mysql connection
* Fix front-end experience issues

---

<!-- 2022-12-22 -->
# V1.9.7 ChangeLog

### Bug Fixes
* An error is reported when the operation authority deletes some instances

---

<!-- 2022-11-28 -->
# V1.9.6 ChangeLog

### Bug Fixes
* Fix the clone user group data is not displayed as empty on the first page

---

<!-- 2022-11-22 -->
# V1.9.5 ChangeLog

### Bug Fixes
* Fix the problem that the user group may select an empty instance

### Optimization Updates
* The recommended action is to only remove instances that the user already has
* The operation list is cached for one minute

---

<!-- 2022-11-08 -->
# V1.9.4 ChangeLog

### Bug Fixes
* Repair chooseip topology components Click to see more missing search keywords

---

<!-- 2022-11-02 -->
# V1.9.3 ChangeLog

### Bug Fixes
* The problem that the operation of user group authorization not associated with resource type does not take effect

---

<!-- 2022-10-12 -->
# V1.9.2 ChangeLog

### New Features
* Merge changes from master branch
* Optimize the sending logic of expired reminder emails

---

<!-- 2022-08-25 -->
# V1.9.1 ChangeLog

### New Features
* Add management api v2

---

<!-- 2022-07-15 -->
# V1.9.0 ChangeLog

### New Features
* User group configuration RBAC policy

---

<!-- 2022-10-10 -->
# V1.8.25 ChangeLog

### Bug Fixes
* Initialize the grading administrator to fix the inconsistency of the customization system

---

<!-- 2022-09-27 -->
# V1.8.24 ChangeLog

### Bug Fixes
* Front-end internationalization bug fixes

---

<!-- 2022-09-27 -->
# V1.8.23 ChangeLog

### Bug Fixes
* Fixed frontend issues

---

<!-- 2022-09-27 -->
# V1.8.22 ChangeLog

### Bug Fixes
* Fixed frontend issues

---

<!-- 2022-09-26 -->
# V1.8.21 ChangeLog

### Bug Fixes
* Fixed frontend clone issue
* Fixed the issue of batch editing of new user groups
* Fixed the problem of duplication of new user group data
* Optimized the picture of the grading administrator
* Optimized version log icon
* Optimized without permission should disable permission handover
* Optimized renewal tips
* Optimized permission handover disabled
* Optimized the font color of the drop-down box
* Fixed the bug that clone can select all instances
* Fixed the bug of inconsistency between authorization and operation

---

<!-- 2022-09-24 -->
# V1.8.20 ChangeLog

### Bug Fixes
* Fixed the bug of custom application renewal check instance number
* Fix front-end experience issues

---

<!-- 2022-09-23 -->
# V1.8.19 ChangeLog

### Bug Fixes
* Fix the display problem of expiration time within 1 day
* Fix the error of expiry time of initial rating administrator members
* Fixed some front-end experience issues

---

<!-- 2022-09-21 -->
# V1.8.18 ChangeLog

### Optimization Updates
* remove permission logger
* Added the function of initializing the grading manager, which requires the environment variable switch BKAPP_ENABLE_INIT_GRADE_MANAGER
* Initialize system manager to add default members
* Front-end experience optimization

---

<!-- 2022-09-09 -->
# V1.8.17 ChangeLog

### Bug Fixes
* Fixed the bug that identity acquisition failed when switching navigation

---

<!-- 2022-09-08 -->
# V1.8.16 ChangeLog

### Optimization Updates
* Optimize the display of expiration time

### Bug Fixes
* Fixed the bug that identity acquisition failed when switching navigation

---

<!-- 2022-09-02 -->
# V1.8.15 ChangeLog

### Bug Fixes
* healthz modifies the celery check timeout
* Fix the bug that the role has only one role and is a system administrator

---

<!-- 2022-09-01 -->
# V1.8.14 ChangeLog

### Bug Fixes
* healthz relies on user management logic optimization
* Fix the bug that the role is only the system administrator page

### Optimization Updates
* The minimum length of user group names is updated to 2 characters

---

<!-- 2022-08-25 -->
# V1.8.13 ChangeLog

### Bug Fixes
* No permission to jump to apply for recommendation permission to remove the user's existing permission
* Update management class api error information
* Multi-window page switching hierarchical administrator permission problem

---

<!-- 2022-08-04 -->
# V1.8.12 ChangeLog

### Bug Fixes
* Modify the header jump logic
* Rating admin delete user group error

---

<!-- 2022-07-28 -->
# V1.8.11 ChangeLog

### Optimization Updates
* Listen to ipv6

### Bug Fixes
* Modifying the basic information of the grading manager only checks the limit on the number of new members

---

<!-- 2022-07-19 -->
# V1.8.10 ChangeLog

### Bug Fixes
* Fix model_event change event fails to execute due to data conversion error

---

<!-- 2022-07-12 -->
# V1.8.9 ChangeLog

### New Features
* Added grading administrator guidelines

---

<!-- 2022-07-01 -->
# V1.8.8 ChangeLog

### Bug Fixes
* Email copy adjustment
* windows window title problem
* Unlimited questions on demand
* Recommended action duplication problem

---

<!-- 2022-06-23 -->
# V1.8.7 ChangeLog

### Optimization Updates
* Unauthorized jump application page optimization
* Navigation adjustment
* Notification email template optimization

---

<!-- 2022-06-21 -->
# V1.8.6 ChangeLog

### Bug Fixes
* Fixed the issue that the newly created associated instance authorization API whitelist-monitoring whitelist does not take effect

---

<!-- 2022-06-16 -->
# V1.8.5 ChangeLog

### Bug Fixes
* Fix the problem that the recommended action cannot be selected by clicking

---

<!-- 2022-05-31 -->
# V1.8.4 ChangeLog

### New Features
* Added management API
   - delete user group policy
   - Support to recycle resource instance permissions of user group policy
   - Paging query the list of graded administrators created by a system
   - Update the authorization scope and basic information of hierarchical administrators
* Enhanced authorization API - support authorization of operation permissions independent of resource instances
* Support regular cleaning of completed model change events

### Optimization Updates
* Cache refactoring, unified use of Django Cache
* Improve the number limit of each data model
   - Resource ID is limited to 36 bits
   - Create up to 100 hierarchical administrators per system
   - The number of members that a rating administrator can add: 100
   - The number of level administrators that a user can join: 100
   - The number of user groups that a level administrator can create: 100
* The paging parameter is adjusted from limit/offset to page/page_size
* Performance optimization - monthly audit table global variable cache
* Swagger refactoring

### Bug Fixes
* Fix front-end related experience issues

---

<!-- 2022-05-16 -->
# V1.8.3 ChangeLog

### Bug Fixes
* When only temporary permissions, my permissions do not show problems
* Temporary permission expiration time selection problem
* request_id parameter error problem

---

<!-- 2022-05-13 -->
# V1.8.2 ChangeLog

### Bug Fixes
* Temporary permissions system switching operation is not clear
* Temporary permissions Polymerization Operation Resources Selection Problems

---

<!-- 2022-05-10 -->
# V1.8.1 ChangeLog

### New Features
* jump without permission to increase recommendation permission

---

<!-- 2022-03-23 -->
# V1.8.0 ChangeLog

### New Features
* temporary permission

---

<!-- 2022-05-19 -->
# V1.7.19 ChangeLog

### Bug Fixes
* Unauthorized jump application has no dependent operation problem

---

<!-- 2022-05-12 -->
# V1.7.18 ChangeLog

### Bug Fixes
* Resource instance selection subordinate search error problem

---

<!-- 2022-04-26 -->
# V1.7.17 ChangeLog

### Bug Fixes
* Fixed Aggregate operation unlimited problem

---

<!-- 2022-04-25 -->
# V1.7.16 ChangeLog

### Bug Fixes
* Fixed Aggregate operation batch copy batch paste

---

<!-- 2022-04-25 -->
# V1.7.15 ChangeLog

### Bug Fixes
* Fixed issues related to selection of aggregation operations
* Approval process operation list supports internationalization

### Optimization Updates
* Django version upgraded to 2.2.27

---

<!-- 2022-04-21 -->
# V1.7.14 ChangeLog

### New Features
* The access system callback query instance list supports passing ancestor instances
* Aggregation operations support aggregating multiple resource types at the same time

---

<!-- 2022-04-19 -->
# V1.7.13 ChangeLog

### Optimization Updates
* The OpenAPI paging parameter is adjusted to page_size/page. For admin.list_group/admin.list_group_member/mgmt.list_group/mgmt.list_group_member, the interface has been opened, compatible with limit/offset

---

<!-- 2022-04-13 -->
# V1.7.12 ChangeLog

### Bug Fixes
* Fixed internationalization related data

### Optimization Updates
* Navigation bar display

---

<!-- 2022-04-07 -->
# V1.7.11 ChangeLog

### Bug Fixes
* Fixed the ITSM display problem of the application form for grading administrators
* Fix front-end merge selection instance problem

### Optimization Updates
* sentry sdk switch

---

<!-- 2022-04-01 -->
# V1.7.10 ChangeLog

### Bug Fixes
* Querying a subject with permission to fix a cross-system resource query error

---

<!-- 2022-04-01 -->
# V1.7.9 ChangeLog

### Bug Fixes
* Fix the error of resource permission management query interface
* Fixed the problem that when adding multiple group permissions to a user group across pages, the permission template selected across the pages would be missing after confirmation.
* Fixed an issue where the application has associated permissions, and the default period will become unchangeable after selecting an instance

---

<!-- 2022-03-24 -->
# V1.7.8 ChangeLog

### Bug Fixes
* Fixed the issue that permissions could not be added under the rating administrator
* Added system access instructions
* Fixed the problem that the user group renewal application callback error was reported due to the absence of the user group

---

<!-- 2022-03-15 -->
# V1.7.7 ChangeLog

### Optimization Updates
* environment property function release

---

<!-- 2022-03-08 -->
# V1.7.6 ChangeLog

### Optimization Updates
* apigw added two open APIs for user-groups/department-groups
* Change the path of the original policy to query the three APIs, add /open/ (but keep forward compatibility: old public=false, add three new ones)
* apigw-manage upgraded to 1.0.2
* apigw configuration backend adjusted from SaaS Web to SaaS API

---

<!-- 2022-03-04 -->
# V1.7.5 ChangeLog

### Optimization Updates
* Connect to APIGateway's SaaS Open API, whose backend is adjusted from bkiam-saas-web to bkiam-saas-api

### Bug Fixes
* Fixed issues related to front-end user group configuration permissions
* Synchronized the organizational structure department and fixed the data error problem of department lft/rght/level

---

<!-- 2022-03-02 -->
# V1.7.4 ChangeLog

### Bug Fixes
* Fix the problem of redis connection leak caused by healthz
* Fixed the problem that the front-end user group configuration permissions did not display the resource type

---

<!-- 2022-02-24 -->
# V1.7.3 ChangeLog

### Bug Fixes
* Fix automatic registration apigateway configuration error

---

<!-- 2022-02-24 -->
# V1.7.2 ChangeLog

### Bug Fixes
* Fix permission template change operation error
* Fix automatic registration apigateway configuration error

---

<!-- 2022-02-21 -->
# V1.7.1 ChangeLog

### New Features
* Regularly clean up unquoted expressions in the background

### Optimization Updates
* Optimize operation audit information
* Optimize log printing
* Optimize SaaS Django configuration, remove blueapps dependency

---

<!-- 2022-01-20 -->
# V1.6.5 ChangeLog

### Bug Fixes
* Fix apigateway register settings error

### Optimization Updates
* ESB and Login slow http request log to component.log
* add creator_authorization_instance white list: bk_job/file_resource

---

<!-- 2021-12-23 -->
# V1.6.4 ChangeLog

### Bug Fixes
* Fix the permission transfer bug
* Fix the script error of automatic registration apigateway
* Fixed an error in the status of the synchronization ITSM application form

---

<!-- 2021-12-21 -->
# V1.6.3 ChangeLog

### New Features
* query authorized subjects

---

<!-- 2021-12-16 -->
# V1.6.2 ChangeLog

### New Features
* opentelemetry tracing

### Optimization Updates
* add permission handover switch

---

<!-- 2021-12-10 -->
# V1.6.1 ChangeLog

### New Features
* Permission transfer

### Optimization Updates
* Front-end refactoring

---

<!-- 2021-12-08 -->
# V1.5.16 ChangeLog

### Optimization Updates
* Do not delete back-end users and departments when the organizational structure is synchronized

### Bug Fixes
* Lock the dependency package typing-extensions version to avoid deployment failure caused by automatic update to the latest version

---

<!-- 2021-12-06 -->
# V1.5.15 ChangeLog

### Bug Fixes
* Fixed the issue that celery_id was obtained as None after LongTask changed synchronization
* Fixed the issue of incompatible action_id with the Scope data structure of the hierarchical administrator authority

---

<!-- 2021-11-30 -->
# V1.5.14 ChangeLog

### New Features
* Support apigateway init with apis and docs

### Optimization Updates
* Automatically update the resource instance name to ignore the defensiveness of the big strategy
* Added bk_nocode whitelist for accessing system management API
* Support to return exception information when calling a third-party interface fails
* User group authorization is adjusted to execute tasks immediately

### Bug Fixes
* Automatically update the resource instance name to be compatible with the access system callback exception
* Solve the authorization exception when the resource instance view is empty

---

<!-- 2021-11-23 -->
# V1.5.13 ChangeLog

### New Features
* Authorized API whitelist supports prefix matching rules
* Automatically update the renamed resource instance in the strategy

### Optimization Updates
* Organization name tips show the full path
* Add line breaks to the log details in the synchronization record of the organizational structure
* The access system management API supports the authorization of unlimited resource instances for the creation of hierarchical administrators and user group authorization interfaces

### Bug Fixes
* Repair the authorization error of the user group template of the hierarchical administrator
* Fix the bug that the permission of the recommended user group for jumping without permission has expired
* The background task cleans up the audit exceptions of the expired members of the user group
* Fix the abnormal handling of the Action model delete event
* Solve the problem of relying on esb when migrate
* Fix the project_view problem causing system authorization error

---

<!-- 2021-11-11 -->
# V1.5.12 ChangeLog

### Optimization Updates
* Add user synchronization records
* After the rating manager modifies the action scope, templates with inconsistent scopes cannot be authorized

---

<!-- 2021-11-04 -->
# V1.5.11 ChangeLog

### Optimization Updates
* The redis version is downgraded to 2.10.6, as a celery broker

### Bug Fixes
* Fix the log configuration of the containerized version
* Fix redis timeout configuration problem

---

<!-- 2021-10-20 -->
# V1.5.10 ChangeLog

### Bug Fixes
* Fix the issue of unauthorized access to the user group member list

---

<!-- 2021-10-20 -->
# V1.5.9 ChangeLog

### Bug Fixes
* Fix long task get results error

---

<!-- 2021-10-20 -->
# V1.5.8 ChangeLog

### Optimization Updates
* Optimize resource callback structure error prompt
* Long-term task retry

### Bug Fixes
* Fix the issue that the updated template is not synchronized to the user group permissions
* Fixed the problem of cookie domain error when port is not 80/443
* Uncheck the corresponding permission instance and report an error
* Fix the bug of tag return value when linking data in the background

---

<!-- 2021-10-11 -->
# V1.5.7 ChangeLog

### Bug Fixes
* Fix the problem of multiple url splicing/causing access errors
* Fix the problem of the wrong address of the front-end personnel list component range

---

<!-- 2021-10-11 -->
# V1.5.6 ChangeLog

### Bug Fixes
* Repair management API-user group custom authorization asynchronously causes continuous authorization failure

---

<!-- 2021-10-08 -->
# V1.5.5 ChangeLog

### Bug Fixes
* User group update template authorization error

---

<!-- 2021-09-29 -->
# V1.5.4 ChangeLog

### Optimization Updates
* Custom permission application supports instance approvers
* The jump application does not merge the user's existing permissions
* The number of instances of the authorization api return strategy

### Bug Fixes
* Fixed the display problem of the renewal email link in the corporate WeChat email
* My permission user group permission check status prompt delete bug
* The business jump permission center applies for permission, the application period cannot be modified
* Fix the display problem of general operation

---

<!-- 2021-09-24 -->
# V1.5.3 ChangeLog

### Bug Fixes
* Fix the front-end ESB address of the v3 Smart package
* Fix ignoring the path bug causing authorization information error
* Fix the display problem of the renewal email enterprise WeChat email link
* Modify my permission user group permission view prompt delete bug
* Fix the unlimited permissions of resource instances, which should not be able to be modified when applying for permissions
* Fix the application permission of the business jump permission center, the application period cannot be modified

---

<!-- 2021-09-15 -->
# V1.5.2 ChangeLog

### Optimization Updates
* Update paas v3 smart settings
* The sharing link is automatically filtered by conditions

### Bug Fixes
* Fixed the issue of error reporting due to partial deletion of policy
* Fixed the issue of authorization error caused by spaces in resource instance name
* Fixed the issue of error in cleaning expired policy
* Fixed the issue of empty approval personnel in the approval process of system manager for approval
* Fixed the issue of error in binding graded manager for creating user groups in management API
* Fixed the issue of subsequent authorization caused by the authorization scope not being aggregated according to the system when creating graded manager in the management API.
* Fix that no permission selected can be saved as a recommended permission template
* Fixed the problem of not being able to select from the configuration platform to the permission center
* Fix that the permission of existing instance should not be included in the limit of new instance application
* Fixed the issue that ordinary users cannot log out when there is no hierarchical administrator

---

<!-- 2021-09-09 -->
# V1.5.1 ChangeLog

### Bug Fixes
* Fixed the issue that the newly created association authorization API failed due to the resource type hierarchy in the registered configuration

---

<!-- 2021-08-30 -->
# V1.5.0 ChangeLog

### Optimization Updates
* SaaS code refactoring
* Open source code optimization

---

<!-- 2021-08-26 -->
# V1.4.30 ChangeLog

### Optimization Updates
* Adjust the list of hierarchical administrator members that ordinary users can manage to join
* Update the whitelist of JOB/BCS new association API

### Bug Fixes
* Access page instance view id, resource type ID uniqueness verification, button position adjustment
* Access page form validation rule repair
* Access page delete operation type value modification
* The screen flickers when accessing the page delete operation
* The problem of jumping errors when switching steps on the access page
* Fix other experience problems on the access page and optimize the copywriting
* Repair the system clients data lost when exporting JSON on the access page
* Fix the error when the authorized scope of the hierarchical administrator is adjusted from all staff to others

---

<!-- 2021-08-13 -->
# V1.4.29 ChangeLog

### Optimization Updates
* Changed the permission expiration reminder email to be sent at 11 o'clock

### Bug Fixes
* User group authorization verification rating manager authorization scope error problem
* Ignoring the path on the authorization page causes the authorization data error problem

---

<!-- 2021-08-11 -->
# V1.4.28 ChangeLog

### Optimization Updates
* Optimized "Ignore Path" to display the full path on the front end

### Bug Fixes
* Fix the error of specific host instances authorized by the operating platform

---

<!-- 2021-08-10 -->
# V1.4.27 ChangeLog

### Optimization Updates
* Optimize resource type ID verification
* Optimize operation ID verification
* Optimize the saving of resource types

### Bug Fixes
* Fix the bug that depends on resource check
* Fix the problem of switching identity
* Fix the icon problem when the model is created

---

<!-- 2021-08-05 -->
# V1.4.26 ChangeLog

### Optimization Updates
* Hierarchical administrators filter problems
* System registration verification rules
* Check the validity of the callback address

### Bug Fixes
* Fix the issue of adding gsekit permission error
* Fix the difference contrast exception

---

<!-- 2021-08-02 -->
# V1.4.25 ChangeLog

### Bug Fixes
* The application form details are rejected for non-applicants to view
* The operation list refuses to be viewed by non-login users

---

<!-- 2021-08-02 -->
# V1.4.24 ChangeLog

### Optimization Updates
* Renewal page interaction optimization

### Bug Fixes
* Fix V2migrate api permission template adds authorization object error bug
* Fix the problem of ignoring the failure of path authorization instance
* Fix the problem that the custom permission application clicks to renew and does not respond

---

<!-- 2021-07-22 -->
# V1.4.23 ChangeLog

### Optimization Updates
* Remove the "permanent" time from the validity period on the application side
* Some known issues have been optimized

### Bug Fixes
* Fix the problem that the expiration time of the automatic filling of dependent operations is empty
* Fixed the problem that the hierarchical administrator failed to save the range of personnel selected
* Fix the issue that the dependent operation instance becomes read-only
* Fix some known issues

---

<!-- 2021-07-20 -->
# V1.4.22 ChangeLog

### Bug Fixes
* Fix the issue that the expiration time of the related action is empty

---

<!-- 2021-07-20 -->
# V1.4.21 ChangeLog

### Bug Fixes
* Fix the security issue of any Origin request in CORS
* Fixed an error on the edit level administrator page
* Fix the problem of editing user group permissions, adding custom permissions is not saved, editing custom permissions again, and adding custom permissions after saving is not displayed on the permissions page
* Fixed the problem that after applying for custom permissions and selecting associated permissions, the post-privileges select the instance, and the pre-privilege instance period is empty and cannot be modified

---

<!-- 2021-07-19 -->
# V1.4.20 ChangeLog

### Bug Fixes
* Fix the problem that the custom permission application cannot be edited after selecting the resource instance when there is a dependency
* Fix the issue that the validity period of custom permissions is empty

---

<!-- 2021-07-15 -->
# V1.4.19 ChangeLog

### New Features
* Hierarchical administrator related operation links support role id parameters; support automatic switching of hierarchical administrator status

### Optimization Updates
* My permission, when there is only one system custom permission, expand by default
* Update the whitelist of ITSM new association API

### Bug Fixes
* Fix the operation problem of deleting hierarchical administrators
* Fix the problem of adding custom permissions and template permissions to the group at the same time
* Fix the display problem of recommended permissions for hierarchical administrators
* Fix the problem caused when the staff input box has spaces

---

<!-- 2021-07-13 -->
# V1.4.18 ChangeLog

### Optimization Updates
* Hierarchical administrator edit mode optimization

### Bug Fixes
* Fix the processing of valid period time when there is no permission to jump
* Fix the issue of permission template update
* Fix the user group add permission dependent operation problem
* Fix the problem that the user group adds the template permission selection instance to report an error
* Fix user group add template permissions
* Fix the editing operation problem of the hierarchical administrator
* Fix the problem that the editing permission template is still displayed after updating

---

<!-- 2021-07-08 -->
# V1.4.17 ChangeLog

### Bug Fixes
* Fix the problem that the user group add template permission selection instance style is disorderly
* Fix the problem that the select box of some instances is not clickable when adding user group permissions
* Fix the optimization of the edit mode of the hierarchical administrator, and the maximum permission range is collapsed by default
* Fix the issue that "editing" is still displayed after the permission template is updated

---

<!-- 2021-07-05 -->
# V1.4.16 ChangeLog

### Bug Fixes
* Fix the user group adding custom permissions to report the validity period error
* Fix the problem of merge selection/batch editing errors
* Fix the problem that user group custom permissions depend on operation
* Fix new operation bugs for hierarchical administrators
* Fix the problem of inconsistency between the authorization scope of hierarchical administrators and user groups
* Fix the problem of switching identities
* Fix the error of deleting custom permissions for user groups
* Fix the front-end bug of renewal mail jump
* Fix the optimization problem of user group permission template deletion style

---

<!-- 2021-07-01 -->
# V1.4.15 ChangeLog

### New Features
* Supports asynchronous delete action and delete action strategy
* User group custom permissions support deleting a certain operation permission function
* Support the function of enabling system access through environment variables

### Optimization Updates
* Optimized editing of user group permissions
* Optimized editing of user group permissions
* The authorized user group OpenAPI supports skipping the verification of the authority scope of the hierarchical administrator

### Bug Fixes
* Fix the copywriting problem
* Fix the problem of automatic expansion of selected instances in batch editing (merge selection)

---

<!-- 2021-06-17 -->
# V1.4.12 ChangeLog

### New Features
* The SaaS side does not have permission to jump to automatically match the user group

### Optimization Updates
* Hierarchical administrator switch identity optimization

### Bug Fixes
* Fix the ID search bug on the application user group page
* Fix the caching problem of search conditions on the application page
* Fix the problem of failure to exit the hierarchical administrator

---

<!-- 2021-06-15 -->
# V1.4.11 ChangeLog

### New Features
* New administrator API-get a user group list under a certain hierarchical administrator
* Support user group authorization API

### Bug Fixes
* Fix the problem that IAM-Engine is not configured to request Endpoint
* Fixed an abnormal problem caused by an error that the user group has been deleted before the application is passed but not ignored

---

<!-- 2021-06-08 -->
# V1.4.10 ChangeLog

### New Feature
* Support build the permission model from page, and genereate the model json

---

<!-- 2021-05-28 -->
# V1.4.9 ChangeLog

### Bug Fixes
* Fix the problem that the SaaS introduced in 1.4.5 deletes the user group, but it is not deleted in the background, which causes the permission error

---

<!-- 2021-05-19 -->
# V1.4.8 ChangeLog

### New Features
* Authorize Open API to support validity period setting
* Batch authorization Open API supports granting unlimited permissions
* Support delete policy subscription event push

### Optimization Updates
* Open API supports error code 1902409 to indicate conflicts of duplicate names, etc.
* My permission page sort adjustment

### Bug Fixes
* Fix the problem of lack of full range judgment when filtering user groups
* Fix the problem that the member of the hierarchical administrator cannot be deleted
* Fix the duplicate display problem of Tips for permission resource instances

---

<!-- 2021-05-13 -->
# V1.4.7 ChangeLog

### New Features
* Automatically generate aggregation action configuration
* Dependent action
* User groups support filtering by role
* ping api

---

<!-- 2021-04-28 -->
# V1.4.6 ChangeLog

### New Features
* Management API-Creating hierarchical administrator and user group authorization support granting unlimited access to some resources
* Management APIs support configuration of the scope of systems that can be controlled and authorized by the system

---

<!-- 2021-04-27 -->
# V1.4.5 ChangeLog

### Optimization Updates
* My Permissions page optimization

### Bug Fixes
* Fix the problem that the number of members of its associated authority template is not updated when the user group is deleted
* Fix the problem that the name can be empty when updating the permission template
* Fix the user group authorization when the new permission template 404
* Fix the problem of reporting an error when adding a new user group with empty group permission

---

<!-- 2021-04-19 -->
# V1.4.4 ChangeLog

### New Features
* New version of permission template
* User Group Custom Permissions

### Optimization Updates
* Optimization of some known issues

### Bug Fixes
* Some known issues fixed

---

<!-- 2021-04-01 -->
# V1.3.6 ChangeLog

### New Features
* New permission template full synchronization script

### Bug Fixes
* Fix the issue of unverified instance selections created by grade manager

---

<!-- 2021-03-25 -->
# V1.3.5 ChangeLog

### New Features
* Added GSEKIT action aggregation configuration

---

<!-- 2021-03-23 -->
# V1.3.4 ChangeLog

### Bug Fixes
* Fix the issue that the hierarchical administrator limit does not take effect
* Fix the issue of invalid instance emptying when applying for permission

---

<!-- 2021-03-18 -->
# V1.3.3 ChangeLog

### Optimization Updates
* Advance de-duplication when adding users to user groups
* Select Action Panel to de-expand for more interactions

### Bug Fixes
* Fix the problem of overstepping the authority when updating the basic information of graded administrators
* Fix the copy-paste error problem when selecting unlimited instances
* Fix the audit error problem caused by v2migrate api authentication
* Fix the cryptographic interpreter logging celery task trace information error reporting problem

---

<!-- 2021-03-09 -->
# V1.3.2 ChangeLog

### New Features
* Grading administrator adds cloning function

### Code Optimization
* Partial code refactoring

### Optimization Updates
* Add a quick selection of operation groups when the grading administrator selects the operation

### Bug Fixes
* Fix the selection period is not effective when batch renewal authority
* Fix the period not effective when applying for custom permission and needing to renew permission

---

<!-- 2021-02-25 -->
# V1.3.1 ChangeLog

### Code Optimization
* Partial code refactoring

---

<!-- 2021-02-20 -->
# V1.3.0 ChangeLog

### New Features
* Support Debug Trace based on Request ID or task ID

### Optimization Updates
* Add a limit of 1000 for the maximum number of user group members

---

<!-- 2021-02-19 -->
# V1.2.15 ChangeLog

### Bug Fixes
* Fix BK_PAAS_HOST with port can not verify through CSRF_TRUSTED_ORIGINS
* Fix the problem of over-limiting the user group of renewal reminder email for graded administrators

---

<!-- 2021-02-02 -->
# V1.2.14 ChangeLog

### Bug Fixes
* Fix the problem that the operation name is not displayed in the ITSM approval document when the custom authority is renewed

---

<!-- 2021-01-28 -->
# V1.2.13 ChangeLog

### New Features
* Operation audit
* Periodically delete expired permission policies

### Optimization Updates
* Update the user group membership expiration reminder of the rating manager

---

<!-- 2021-01-25 -->
# V1.2.12 ChangeLog

### Optimization Updates
* Update the approval callback address to an intranet address
* Rating Manager name uniqueness check

### Bug Fixes
* Fix the problem of hierarchy selection during permission configuration
* Fix the problem of incorrect display of the validity period of application documents

---

<!-- 2021-01-20 -->
# V1.2.11 ChangeLog

### Bug Fixes
* Fix the application of updating rating manager exception
* Fix common operation selection grouping exception

---

<!-- 2021-01-15 -->
# V1.2.10 ChangeLog

### Bug Fixes
* Fix the update rating manager exception

---

<!-- 2021-01-14 -->
# V1.2.9 ChangeLog

### New Features
* Instance authorization-related APIs add whitelist restrictions
* Internationalized time zone support

### Optimization Updates
* Edit templates and hierarchical administrators to add resource instance IDs and Name checks
* Side sliding closure adds secondary confirmation interaction
* Added permissions do not determine whether they are expired or not
* Enum class code refactoring optimization
* Celery Healthz Optimization

### Bug Fixes
* Fixed the problem that users do not have abnormalities when the authentication-related interface judges super privileges
* Fixed the problem of wrong display of table data when merging operations when creating a new permission template

---

<!-- 2021-01-14 -->
# V1.2.8 ChangeLog

### Bug Fixes
* Fix the problem of migration failure caused by user group not binding hierarchical administrator when migrating V2 data to V3

---

<!-- 2020-12-31 -->
# V1.2.7 ChangeLog

### New Features
* Customized application to add operation grouping function

### Optimization Updates
* Sync admin user and add as super admin member when default Migrate DB
* Feedback links support multiple version differentiation
* No permission to jump to locate the selected operation
* Topology instances support batch selection by pressing and holding shift

### Bug Fixes
* Fix the problem of no authentication of some APIs when setting the approval process
* Fix the problem of incorrect submission of application documents for users without organizational affiliation
* Fix the problem of not taking effect when actively renewing user group members
* Fix the problem that the status of document withdrawal is not displayed
* Fix the problem of information leakage of the new approval process copy prompt
* Fix the problem of inconsistency between the front and back ends of verification rules when creating new user group names
* Fix the problem that the approval process setting page is not updated after role switching
* Fix the resource instance ID and Name error when selecting a resource with unrestricted hierarchy
* Fix the problem of not resetting the query conditions when selecting an instance for the second time in aggregation

---

<!-- 2020-12-24 -->
# V1.2.6 ChangeLog

### New Features
* Add newbie guide
* Add policy expiration email reminder

### Optimization Updates
* Optimize authorization without updating if the existing policy contains a new policy
* Add default group non-deletion logic for operation groups

### Bug Fixes
* Fix the DB contention lock issue that may occur when deleting policy instances
* Fix the error when choosing a specific instance for permission template aggregation instance
* Fix the sidebar that triggers the opening of the selected instance when you click Batch Paste for the selected instance

---

<!-- 2020-12-17 -->
# V1.2.5 ChangeLog

### New Features
* Application support revocation
* Support users' user groups with custom permission renewal
* Support for renewal of user group membership for administrators
* Select instances to add paste and bulk paste for aggregation and non-aggregation
* Support initialization with ITSM default process
* Support query callback to access the system's resource instance name cache
* Support access to system registration function switch

### Optimization Updates
* Support for differentiating product documentation links by feature page
* Add more detail links to the grading administrator page
* Query parameters for front-end cached page form data
* Interaction optimization of permission selection instance aggregation operations
* All permission submissions verify that the resource instance ID and Name match
* Default unattributed user groups and templates migrated to Super Admin

### Bug Fixes
* Repair the error in displaying the switch status of aggregation operation when editing the hierarchical administrator
* Repair the setting of default approval process data does not take effect in time

### Package Dependencies
* [ee] bk_itsm >= 2.5.7.235 ([ce] bk_itsm >= 2.5.7.237)

---

<!-- 2020-12-03 -->
# V1.2.4 ChangeLog

### New Features
* My Approval Menu, user clicks to jump to ITSM Personal Approval Center
* Super Administrators can transfer user groups out to a designated hierarchical administrator
* Batch Authentication API

### Optimization Updates
* Removal of Newbie Guidelines
* The hierarchical administrator details the system's operating privileges to increase unfold and collapse interaction
* Hierarchical administrator detailsSystem operation permission listAdd filtering by system
* Display its instance name directly when selecting a single instance
* Optimize caching of subject action
* Optimize the role of super powers during authentication

### Bug Fixes
* Fix search topology instance cache error
* Hierarchical Administrator Details Member List Edit Button Style Fixes
* Fix the problem of instance data mismatch when switching between unused views when there is a range limitation in multiple instance views in the new permission template
* New Permission Template Property Selection Box Disable Problem when Super Admin
* New hierarchical administrator selected to fix instance data error when saving the same operation id across systems

---

<!-- 2020-11-26 -->
# V1.2.3 ChangeLog

### New Features
* Hierarchical administrator applies for modification

### Optimization Updates
* Create hierarchical administrators to support generating dependent operations

### Bug Fixes
* Permission template modified some resources but not deleted bug
* Several front-end bug fixes

---

<!-- 2020-11-20 -->
# V1.2.2 ChangeLog

### New Features
* Support the addition of new users in real time within 1 minute

### Optimization Updates
* Initialised Super Admin approach adjusted from API calls to Migrate DB on deployment
* The individual instances are displayed directly when applying for permission to select them
* Product documentation link updates
* New permission template Search should be adjusted to front-end search when restricted data exists for the instance
* Login window resizing

### Bug Fixes
* Fix problem with occasional permission requests where a specific instance is selected but a null value is passed

---

<!-- 2020-11-18 -->
# V1.2.1 ChangeLog

### Optimization Updates
* Initial action aggregation optimization
* Optimized display of approval nodes when displaying process list
* Logout window style optimization
* Automatically refreshes the page when the currently logged in user is deleted by Super Admin
* Show specific instances of a single instance directly when applying for permission to select it.

### Bug Fixes
* Fix open api role auth error where super manager not exists
* Fixed the bug that the copy instance paste button is displayed when requesting permissions.

---

<!-- 2020-11-17 -->
# V1.2.0 ChangeLog

### New Features
* Support for Rating Manager functions
* Approval process interface with itsm (support for approval notification)
* Support for super administrator and system administrator settings
* Multi-operation instance merge selection
* Support for saving frequently used operations (administrator function)
* Support for switching administrator roles
* Support approval process configuration

### Optimization Updates
* Site wide search optimization

---

<!-- 2020-12-07 -->
# V1.1.46 ChangeLog

### Bug Fixes
* Fix search topology instance cache error

---

<!-- 2020-11-12 -->
# V1.1.45 ChangeLog

### New Features
* User logout support

### Optimization Updates
* Update product documentation links

### Bug Fixes
* Repair the problem of empty description when switching system with new permission template.
* Repair the problem of saving exception when editing basic information of user group.

---

<!-- 2020-11-09 -->
# V1.1.44 ChangeLog

### Bug Fixes
* Fix the error of adding unlimited front-end processing instance selection.

---

<!-- 2020-11-04 -->
# V1.1.43 ChangeLog

### New Features
* New product documentation link entry

### Optimization Updates
* Resource instance search first level error message optimization
* Table search box front-end optimization

---

<!-- 2020-10-22 -->
# V1.1.42 ChangeLog

### Bug Fixes
* Fix the add tag problem of data migration interface

---

<!-- 2020-10-20 -->
# V1.1.41 ChangeLog

### Bug Fixes
* Fix the problem of entering the iam saas exception when new users are not synced.
* Fix the problem of authorization API error when new users are not synced.

---

<!-- 2020-10-14 -->
# V1.1.40 ChangeLog

### Optimization Updates
* Topology Instance Search Front End Optimization Error Message
* Remove Resource Instance Paste

---

<!-- 2020-10-01 -->
# V1.1.39 ChangeLog

### Optimization Updates
* Synchronized Organizational Architecture Distributed Lock Failure Prompt Failure and Logging
* Topology Resource Instance Search Front End Display Details Optimization

---

<!-- 2020-09-28 -->
# V1.1.38 ChangeLog

### New Features
* Support for search of topological instances

### Optimization Updates
* Synchronized Organizational Architecture Distributed Lock Failure Prompt Failure and Logging

### Bug Fixes
* Fix the problem of incomplete pull due to sorting problem when synchronizing organizational structure pagination to get departments and users.

---

<!-- 2020-09-25 -->
# V1.1.37 ChangeLog

### Optimization Updates
* Exceptional error messages and log optimizations for interfaces related to resource queries for access to the system

### Bug Fixes
* Repair the problem that the authorization of new related properties does not take effect.

---

<!-- 2020-09-23 -->
# V1.1.36 ChangeLog

### New Features
* Support the ability to paste resource instances

### Optimization Updates
* Topology instance selection panel supports dragging
* No drop-down list is needed when there is only one instance view.

### Bug Fixes
* Fix the problem of topology instance selection without sub-level resource limit.

---

<!-- 2020-09-18 -->
# V1.1.35 ChangeLog

### Update
* [ bugfix ] New associated permissions, instance name display error bug
* [ optimization ] Access system callback error message optimization

### Feature
* [ Feature ] New user group membership matching added function

---

<!-- 2020-09-14 -->
# V1.1.34 ChangeLog

### Bugfix
* [ bugfix ] My permissions - wrong time to join user group
* [ bugfix ] Application or configuration permission page - icon and text overlap in time selection customization

---

<!-- 2020-09-10 -->
# V1.1.33 ChangeLog

### Feature
* [ feature ] My permissions page user group permissions increase the display of group members

---

<!-- 2020-09-08 -->
# V1.1.32 ChangeLog

### Feature
* [ feature ] Resource creator action support attribute authorization

---

<!-- 2020-09-07 -->
# V1.1.31 ChangeLog

### Feature
* [ feature ] `Resource instance authorization increases the number of instances limit`

---

<!-- 2020-06-22 -->
# V1.1.1 ChangeLog

### Feature
* [ feature ] `Instance view of resource selection supports configuration ignore path`

> The path is ignored when the resource configuration permission is supported, which is used to only authenticate the ID of the resource

---

<!-- 2020-06-19 -->
# V1.1.0 ChangeLog

## BKIAM-V3 V1.1.0 goes online ！

### Feature

* [ feature ] `Apply` According to user scenarios, we support to apply by permission templates, join  groups, and
 customize application：

> `Apply by permission template` When users need permissions for a single system role, he can search for a template directly without relating an instance
>
> `Join the groups` When users need permissions of multiple systems, they can quickly obtain the permissions by joining groups
>
> `Custom application` Custom application permission is an advanced features, users can freely check the permission required for application
>
> - Support the echo of existing permissions
> - Support comparison of permissions change
> - Support topology selection the instances
> - Support attribute filtering instance

* [ feature ]  `My Permissions`

> The display of all personal permissions, including custom application permissions , permissions applied by permission templates, permissions to join groups, and permissions to inherit organizations
>
> Support to recovery the instance permissions
>
> Support to exit groups

* [ feature ] `My Application`

> All application documents initiated by individuals

* [ feature ] `My Approval`

> All documents that individuals need to approve

* [ feature ] `Permission Templates`

> The permission template of  V3 is an instantiated template instance, and changes of the permission template can also be synchronized to authorized users

* [ feature ] `User or organization permissions management`

> Administrators can manage the permissions of users or organizations through the organizational structure

* [ feature ] `Groups`

> Groups are associated with permission templates, and groups can selectively synchronize the updated permission templates
>
> Groups can add users or organizations, users in the group will inherit the permissions of the group
