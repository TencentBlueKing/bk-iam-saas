<!-- 2025-11-21 -->
# V1.10.48 Version Update Log

### Features
* Permission initialization for business-based space management now supports the bksam system
* OpenAPI supports querying user groups and cleaning group members under system management spaces via API
* My Management Space, Management Space, and Space Information modules now support batch unlimited operations
* My Management Space, Management Space, and Space Information now support batch unlimited aggregation, batch copy and paste
* Custom permission policy applications for multiple resource types now support approval by business-based space management administrators

### Fixes
* Fixed privilege escalation issue on pages after switching high-privilege users to low-privilege users

---

<!-- 2025-10-14 -->
# V1.10.47 Version Update Log

### Features
* OpenAPI - `management_grade_manager_groups` now supports returning metadata fields such as updater and update time.
* Disabling notification for project renewals in BlueKing for deactivated projects.
* User organization options now allow filtering group members by validity period.
* Added Django command for super admin user authorization.

### Fixes
* Fixed an issue where the application form status was not updated after approval callback due to unsupported transactions, leading to execution authorization problems.
* Fixed an issue where instances of dependent operations were empty after editing resource instances in a standard IT operation within a user group.
* Fixed inconsistencies of role types during role cleanup.

---

<!-- 2025-08-21 -->
# V1.10.46 Version Update Log

### Features
* Clean up permissions before the user-specified time

---

<!-- 2025-08-06 -->
# V1.10.45 Version Update Log

### Features
* Added Japanese internationalization support for Blueking Devops
* Enhanced XSS protection optimization

---

<!-- 2025-05-28 -->
# V1.10.44 Version Update Log

### Fixes
* Fixed an issue where login authentication was executed after role identity authentication, potentially leading to security issues if the role identity session was leaked.
* Fixed an exception when deleting an administrator in the secondary management space of the Grade Manager.
* Optimized the style of the no-permission application table and handled the deduplication issue of temporary permission application aggregation.

---

<!-- 2025-05-15 -->
# V1.10.43 Version Update Log

### Features
* Added support for TLS encrypted connection configurations for MySQL, Redis, RabbitMQ, and other components.
* Revised user group module interaction in the permission template editing to address the issue of being unable to fully submit user groups in the previous version.
* Introduced debounce search for attribute condition search across the platform to address continuous triggering of searchLoading in the component library.
* Differentiated the display format for system administrators and other types of administrators.

---

<!-- 2025-04-17 -->
# V1.10.42 Version Update Log

### Feature Enhancements
* The compatibility gateway's lower version does not support resource configuration for the OpenAPI 3.0 protocol

---

<!-- 2025-04-10 -->
# V1.10.41 Version Update Log

### Fixes
* Fix the abnormal flow of custom permission auditing in dbm

---

<!-- 2025-04-01 -->
# V1.10.40 Version Update Log

### Features
* Added document link environment variable BK_CE_URL
* Added OpenAPI for single action attribute authorization
* Added OpenAPI for batch renewal of user groups
* Added OpenAPI related to permission templates

### Feature Enhancements
* Platform management and management space resource permission management share the same business logic
* Rectification of the sidebar under the management space navigation bar
* Added administrator identity for quick search and positioning on all pages requiring administrator verification

### Fixes
* Fixed uncleaned SaaS table data for departed users
* Fixed missing audit logs due to bulk_create not triggering signals
* Fixed abnormal select box style in the approval process management -> join user group approval process

---

<!-- 2025-02-13 -->
# V1.10.39 Version Update Log

### Features
* Added event communication for the renewal of embedded pages in Blue Shield.
* When applying to join a user group, if the secondary resource owner leaves, the request is escalated to the primary administrator for approval.
* Secondary management spaces now support editing personnel and resource instance authorization scopes.
* Added automatic association of main operation with operation instances when cloning or editing secondary management spaces.
* The page for redirecting when switching administrator identity now includes authorization boundaries and secondary management spaces.
* Added a reason field to authorization boundaries.
* Pagination added to the secondary management space in the management space role selector.
* The Open API member list interface now supports retrieving the time members joined user groups.
* Blue Shield business scenarios that expand the authorization personnel boundary no longer require interface calls to verify authorization scopes.
* Blue Shield now supports limiting organizational structure business selection via environment variable injection.
* Added pages requiring custom styling for adding authorization personnel boundaries.

### Feature Enhancements
* Unified parameter coordination for Blue Shield requirements.
* Optimized menu for secondary management spaces.
* Enhanced compatibility for permission templates under public components in secondary management spaces.

### Fixes
* Fixed an issue where table associated operation data would be emptied if the main operation had associated operations and the interface response data was empty.
* Resolved the "undefined" issue when handling authorization scopes with only custom attributes and no resource instances.
* Fixed style misalignment issues in fine-grained permission applications.
* Corrected the redirection issue where a hierarchical administrator would need to switch to the user group page when editing authorization boundaries.
* Removed permission template editing in management spaces.
* Fixed an issue where editing resource instances in secondary management spaces would sometimes display selected instances as disabled.
* Addressed whether the primary operation's resource authorization scope is consistent with the associated operation in aggregation scenarios.
* Fixed occasional table style misalignment issues in the resource instance table module for administrator identities.
* Resolved the 8-hour discrepancy issue in the validity period when users join a user group.

---

<!-- 2024-11-12 -->
# V1.10.38 Version Update Log

### Feature Enhancements
* The management space personnel selector edit component supports re-editing the scenario after being set to empty by default (the administrator has left).

---

<!-- 2024-11-07 -->
# V1.10.37 Version Update Log

### Fixes
* Fixed an error when previewing difference comparisons if a user group has no resource instances and attribute conditions.
* Resource instance difference comparisons can only be previewed if the user group module exists and the user group itself exists.
* Fixed an issue where incorrect child_type values prevented the expansion of non-terminal node topologies.
* Resolved an issue where, in the main operations of user groups and secondary management spaces, removing unrestricted resource instances from associated operations occasionally caused authorization boundary overflows.

---

<!-- 2024-10-11 -->
# V1.10.36 Version Update Log

### Features
* User group authorization now supports associating permission instance scopes across different system resource types

### Feature Enhancements
* Updated all documentation center redirect links to the latest standards.

---

<!-- 2024-09-27 -->
# V1.10.35 Version Update Log

### Fixes
* Use pymysql to replace mysql-client

---

<!-- 2024-09-25 -->
# V1.10.34 Version Update Log

### Features
* Bk Devops User Group Permissions: Added support for adding, deleting, and editing event communication within embedded iframe pages, enhancing page interaction and data synchronization.

### Feature Enhancements
* Documentation Updates: Updated product documentation and the links in "My Management Space" to the latest versions, ensuring users have access to the most current help documents and guides.
* Instance View Optimization: Optimized the interface for fetching data when the last node in the instance view and the current topology level's child_type is empty, ensuring unnecessary data retrieval is avoided.

### Fixes
* Path View Discrepancy: Fixed occasional issues where the number of instances displayed in the path view layer did not match the actual number of authorized instances.
* Topology Data Flattening: Fixed issues where the flattened structure of topology data could not distinguish instance scopes, which could cause data inconsistencies when a hierarchical administrator's authorized instance scope was the parent level, but automatically associated subsets when selected.
* Breadcrumb Navigation: Fixed issues with breadcrumb navigation in "My Management Space" that caused it to return to incorrect pages.

---

<!-- 2024-09-02 -->
# V1.10.33 Version Update Log

### Fixes

* Added system filter to the resource instance search when applying to join a user group.
* Removed the refresh icon from the permission template addition in group permissions.
* Compatible with non-root path deployment in containerized external environments.

---

<!-- 2024-08-22 -->
# V1.10.32 Version Update Log

### Fixes

* Fixed apigw resource definition yaml error

---

<!-- 2024-08-22 -->
# V1.10.31 Version Update Log

### Features

* Super Admin API: Added template list and the ability to add members to user groups.

### Fixes

* Embedded pages in BlueKing now hide the link to the authorization boundary entry.
* Fixed multiple escapes of the redirect URL upon logout.

---

<!-- 2024-08-14 -->
# V1.10.30 Version Update Log

### Features

* Added support for quick navigation to the admin menu page when the user has admin rights and the current page is under the personal workstation staff role scenario.
* Upgraded global configuration version to support distinct wording for product name and title.

### Fixes

* Fixed an issue where the user group -> hierarchical admin permissions occasionally auto-associated instances outside the authorized scope.
* Fixed an issue with custom permission requests where batch editing operations displayed abnormal resource instances.
* Fixed an issue where secondary admin -> hierarchical admin permissions occasionally auto-associated instances outside the authorized scope.
* Fixed an issue where deleting the last template data on the last page of the personnel template prompted that the data did not exist.
* Fixed an issue where the number of selected operations disappeared when viewing already selected data in custom permissions.
* Fixed an issue where the frontend did not validate spaces input in recommended permissions when creating a new permission template and clicking save.
* Fixed an issue where custom permissions in the user group resource instance table, after aggregation, occasionally resulted in `resource_group` being empty when re-aggregating after selecting a permission template.
* Fixed an issue where instances could not be deleted when the custom permission view instance resource component had multiple resource type tabs.
* Fixed an issue where new users with no permissions were redirected to the permission center with resource instances set to unrestricted instead of empty.
* Modified the expiration period of the internationalization language cookie to default to one year.

---

<!-- 2024-06-25 -->
## V1.10.29 Version Update Log

### Features

* Added an npm integration plugin for unified management of configuration items like logo, footer, and title.
* Replaced the batch aggregation method for all platform resource instances from the switch component to a custom tab component.
* Enhanced the platform property view to be compatible with individual custom attribute sets from connected systems that require a personnel selector component.
* Updated the layout of system addition and operation pages across the platform (refresh functionality is now open to all users, not just hierarchical administrators).

### Fixes

* Fixed the issue where applying for a user group—>where permissions to apply for permissions and commonly recommended permissions should hide operations provided by the connected system if no permissions exist.
* Fixed the issue where switching systems during custom permission applications did not clear the resource instance table data.
* Fixed the issue where editing user group permissions—>modifying the resource instance content and then clicking cancel had no effect.

---

<!-- 2024-05-13 -->
## V1.10.28 Version Update Log

### Features

* Configuration of permission expiration reminder notification strategy
* Added enterprise WeChat as an option for permission expiration reminder notifications
* Modified small window login iframe method and added support for integrated uniform iframe loading mode via npm
* Added a management space filter in resource instance search for joining user group applications
* New API - Create custom approval form for permission application, supporting custom approval content

### Fixes

* Fixed issue where directly accessing the management space and user group details page would redirect to the corresponding list page
* Fixed data loss when searching resource instances with keywords
* Fixed issue where personnel templates associated with user groups could be successfully deleted in batch
* Fixed issue where pagination buttons displayed abnormally after scrolling to the bottom on the template association user group page
* Fixed issue where the success popup could not close automatically after deleting super administrator members
* Fixed issue where the user group count would not display after deleting a user group until the page is refreshed
* Fixed issue where custom pagination could not be set for system filtering when applying for renewal of custom permissions
* Fixed issue where incorrect `type` values occurred due to having only one layer of topology but multiple resource types

---

<!-- 2024-04-25 -->
# V1.10.27 Version Update Log

### Fixes

* System-registered non-apply operations take effect for "My Management Space"
* Add support for fuzzy search of members (resolves the issue of not being able to search for users with login domains)

---

<!-- 2024-04-12 -->
# V1.10.26 Version Update Log

### Feature Enhancements

* Dependency version upgrades

### Fixes

* Fixed issue with scheduled organization synchronization task becoming ineffective

---

<!-- 2024-04-11 -->
# V1.10.25 Version Update Log

### Features

* Added the ability to manage permissions for desired users/departments within the management space.
* System administrators can now query personnel with permissions.
* System administrators can now edit sensitivity levels.

---

<!-- 2024-03-01 -->
# V1.10.24 Version Update Log

### Feature Enhancements

* Resource instance IP selector revision

### Fixes

* Fixed my permissions ->Add cross page selection to user group permissions
* Fixed my permissions ->Add cross page selection for administrator handover

---

<!-- 2024-02-23 -->
# V1.10.23 Version Update Log

### Fixes

* Fixed an issue where the user group only added permission templates, and the table data was cleared after quick close.
* Fixed an issue where adding instances to permission templates couldn't be pasted in bulk.
* Fixed role_id error for some secondary administrators on the Blue Shield embedded page.
* Added hidden field filtering for system operations hidden in Blue Shield user group embedded pages.

---

<!-- 2024-01-30 -->
# V1.10.22 Version Update Log

### Fixes

* Fixed an issue in custom permission requests where the edit display fails to show selected resources instances of unlimited type data.
* Fixed a problem in user groups where adding group permissions with varying path quantities resulted in an error message indicating that the hierarchical link list cannot be empty.
* Improved the organization structure personnel selector to hide the selected count when it is 0.

---

<!-- 2024-01-22 -->
# V1.10.21 Version Update Log

### Feature Enhancements

* Integrated with the BlueKing Message Notification Center

---


<!-- 2024-01-16 -->
# V1.10.20 Version Update Log

### Optimization Updates

* Optimized content for permission application forms.

### Fixes

* Fixed an issue where the maximum authorization scope selection within the Blue Ocean embedded page did not allow user selection after choosing an organization.
* Fixed an problem where adding group permissions - adding operations and permission templates first, then canceling operations or reducing the number of permission templates, resulted in no display.
* Fixed an issue where the content of the personnel selector editing component was empty, and re-adding would reset the data from the previous instance.

---

<!-- 2023-12-26 -->
# V1.10.19 Version Update Log

### Features

* Added a personnel template menu under the management space navigation bar.
* Added the ability to associate personnel templates in user group details.
* Added the ability to associate personnel templates in "My Permissions" under the personal workspace.
* Added the ability to associate personnel templates and join permissions of the corresponding user group in the organization details under the "User" menu in platform management.
* Custom permission dropdown list now supports bookmarking commonly used systems.
* Modified the error message when attempting to add more than 100 members to an applied user group.
* Added a personnel template option to the organization member selector, and manually input options now support special character separation as defined, with support for a maximum of 100 members at a time.
* Added the option for full authorization scope in the embedded Blue Shield maximum authorization range dialog page, supporting authorization scope for all members.

### Fixes

* Fixed the issue where the total number of items in the transfer list interface was not synchronized with the total number obtained in the interface after searching for sensitivity levels.
* Fixed the issue where clicking any placeholder in the textarea component triggers a blur event.

---

<!-- 2023-11-28 -->
# V1.10.18 Version Update Log

### Fixes

* Fixed a bug where authorization scope validation was not required in the organizational structure selector for IAM system and Blue Shield system
* Fixed an issue where the calculation of renewal timestamps for user group members resulted in incorrect display of days due to rounding off floating point numbers
* Added sensitive level business block to the audit module
* Fixed an issue where filtering by all levels in the sensitive level selection was not working
* Resolved an error message length issue when there were no custom permissions in the IAM permission center page within the Blue Shield system
* Fixed the inability to batch edit newly created user groups when cloning user groups for the first time
* Fixed a bug where the submit button was disabled in the user module's organizational structure when no personnel were added
* Fixed an issue where the table component did not adapt its height when opening the console
* Added functionality to exit My Management Space

---

<!-- 2023-11-16 -->
# V1.10.17 Version Update Log

### Optimization Updates
* Sensitive level requirements
* Custom permission application - Add custom message when adding user groups exceeds 100
* User module - Add resource instance search for user types
* User module - Add ability to add members to organizational structure

### Fixes
* Frontend configuration to hide operations on certain pages (no longer handled through backend flags)
* No response when administrator tries to add duplicate members (show tip when unable to add members)
* Resolve issue with staff role showing no permissions in person selector

---

<!-- 2023-11-07 -->
# V1.10.16 Version Update Log

### Optimization Updates
* Optimized handling of multiple API calls in the sidebar for adding systems and operations, addressing aggregation issues.
* Added version declaration at the bottom of the "My Permissions" list.
* Added support for batch deletion and renewal of members in user groups across multiple pages.
* Redesigned the organization structure member selector.
* Made the product documentation link a dynamic configuration item.
* Added custom error message for exceeding 100 requests to join a user group.
* Added group renewal for expired user groups in the "Apply to Join User Group" feature.

### Fixes
* Fixed an issue where creating or cloning a user group and re-editing the group permissions without changing the operations would not display the previously selected options.
* Fixed the inability to batch paste multiple unrestricted operations under a hierarchical administrator.
* Fixed an error in the aggregation of individual operations in batch operations, resulting in missing authorization scope data.
* Fixed the lack of synchronization of dependency operations when editing authorization boundaries or editing management spaces.
* Fixed an issue where batch paste would show unlimited content when there were no copyable attribute conditions.
* Fixed a styling issue where a box appeared after deleting all custom permissions.
* Fixed a blank page issue caused by batch editing operations with no intersection.
* Fixed incomplete update information prompt for user groups after editing associated instances in permission template editing.
* Fixed the failure to clear old data when there are no selected instances in the management space module.
* Fixed the inability of the custom date selector to display the selected days based on the timestamp.

---

<!-- 2023-09-19 -->
# V1.10.15 Version Update Log

### Fixes
* Added support for BlueShield in user search for My Permissions.
* Modified the second-level administrator name change to be case-insensitive.
* Adjusted the synchronization strategy for adding new users.

---

<!-- 2023-09-14 -->
# V1.10.14 Version Update Log

### Fixes
* "Not Requestable" now takes effect in automatic recommendation rules.
* BlueShield My Permissions page now displays BlueShield projects only in search criteria.
* Fixed an issue with CDN hashing for static files.

---

<!-- 2023-09-05 -->
# V1.10.13 Version Update Log

### Features
* Added "not available for application" attribute setting to user groups

### Optimization Updates
* Synchronized the latest message specification and searchSelect specification across all platforms
* Users can now exit multiple user groups at once
* User group permission renewal page now displays description, administrator, and management space data
* Added member addition, member copying, and organizational structure functions to user groups
* Added search function to "My Permissions" page
* Removed query type filter from resource permission management, default query type is now instance permission

### Fixes
* Fixed issue where clicking on renewal email link for Blue Shield project administrators resulted in blank webpage content
* Fixed issue where user group member renewal effective time stamp calculation was incorrect
* Fixed issue where Blue Shield permission transfer check for "disabled" was incorrect, added pagination to user group permission transfer and administrator transfer
* Fixed issue where modifying project name still resulted in timeout
* Fixed issue where user application for multiple groups resulted in error due to long title.

---

<!-- 2023-07-31 -->
# V1.10.12 ChangeLog

### Features
* Custom permissions can be configured to allow multi-level administrator approval.
* Batch unlimited permissions have been added to user group creation, cloning, and permission addition.
* Batch copying of users and organization members has been added to user group management.

### Fixes
Fixed an issue where clicking on "synchronize" in the user module->user type would result in a third-party interface exception.

---

<!-- 2023-07-26 -->
# V1.10.11 ChangeLog

### Features
* Switching ESB interface login, supporting ESB authentication for application permissions.

---

<!-- 2023-07-17 -->
# V1.10.10 ChangeLog

### Features
* Add department display to user group member list
* Add permission details to expired permission list
* Allow optional selection for aggregated operations
* Allow level 1 administrators to directly access level 2 administrators

---

<!-- 2023-07-07 -->
# V1.10.9 ChangeLog

### Fixes
* Fixed the issue that the dependency operation was not synchronizing data when adding attribute conditions for user group permissions.
* Fixed the issue that the system administrator member editing was abnormal, and the input box of the system administrator member was abnormal.
* Added the requirement to add or remove all operation instances under a single system for "My Permissions".
* Adjusted the layout of the module for deleting and viewing user group permissions.

---

<!-- 2023-07-05 -->
# V1.10.8 ChangeLog

### Fixes
* Fixing front-end internationalization issues

---

<!-- 2023-06-27 -->
# V1.10.7 ChangeLog

### Features
* When deleting an instance with a custom permission, delete the instance that is dependent on the permission at the same time

### Fixes
* ITSM bill of lading form field internationalization
* Language switching is set to BK_DOMAIN
* Hierarchical administrator synchronization permission user group name internationalization

---

<!-- 2023-06-21 -->
# V1.10.6 ChangeLog

### Fixes
* Fixed the issue where the default workflow for the graded administrator was empty
* Fixed the issue with the audit log record table create name

---

<!-- 2023-06-07 -->
# V1.10.5 ChangeLog

### Features
* Applying for user group permissions can be done by operating and searching user groups in the instances

### Optimization Updates
* Optimize the associated permission deletion logic

---

<!-- 2023-06-02 -->
# V1.10.4 ChangeLog

### Features
* Added BCS automatic initialization of administrator user group, making it easier for administrators to set up the system.

### Fixes
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

### Fixes
* The open api creation permission application form increases the expiration time
* Fix the unprocessed permission removal when submitting a custom permission application

---

<!-- 2023-05-10 -->
# V1.10.0 ChangeLog

### Features
* Support secondary management space feature

---

<!-- 2023-03-28 -->
# V1.9.10 ChangeLog

### Features
* Add temporary permission switch
* Modify the maximum number of tiered administrators that can be created in the api to 500

---

<!-- 2023-02-20 -->
# V1.9.9 ChangeLog

### Fixes
* Management api user group authorization is not associated with resource instance conversion bug

---

<!-- 2023-01-31 -->
# V1.9.8 ChangeLog

### Features
* Initialize rating administrator update custom action

### Fixes
* Repair the healthz interface to actively close the mysql connection
* Fix front-end experience issues

---

<!-- 2022-12-22 -->
# V1.9.7 ChangeLog

### Fixes
* An error is reported when the operation authority deletes some instances

---

<!-- 2022-11-28 -->
# V1.9.6 ChangeLog

### Fixes
* Fix the clone user group data is not displayed as empty on the first page

---

<!-- 2022-11-22 -->
# V1.9.5 ChangeLog

### Fixes
* Fix the problem that the user group may select an empty instance

### Optimization Updates
* The recommended action is to only remove instances that the user already has
* The operation list is cached for one minute

---

<!-- 2022-11-08 -->
# V1.9.4 ChangeLog

### Fixes
* Repair chooseip topology components Click to see more missing search keywords

---

<!-- 2022-11-02 -->
# V1.9.3 ChangeLog

### Fixes
* The problem that the operation of user group authorization not associated with resource type does not take effect

---

<!-- 2022-10-12 -->
# V1.9.2 ChangeLog

### Features
* Merge changes from master branch
* Optimize the sending logic of expired reminder emails

---

<!-- 2022-08-25 -->
# V1.9.1 ChangeLog

### Features
* Add management api v2

---

<!-- 2022-07-15 -->
# V1.9.0 ChangeLog

### Features
* User group configuration RBAC policy

---

<!-- 2022-10-10 -->
# V1.8.25 ChangeLog

### Fixes
* Initialize the grading administrator to fix the inconsistency of the customization system

---

<!-- 2022-09-27 -->
# V1.8.24 ChangeLog

### Fixes
* Front-end internationalization bug fixes

---

<!-- 2022-09-27 -->
# V1.8.23 ChangeLog

### Fixes
* Fixed frontend issues

---

<!-- 2022-09-27 -->
# V1.8.22 ChangeLog

### Fixes
* Fixed frontend issues

---

<!-- 2022-09-26 -->
# V1.8.21 ChangeLog

### Fixes
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

### Fixes
* Fixed the bug of custom application renewal check instance number
* Fix front-end experience issues

---

<!-- 2022-09-23 -->
# V1.8.19 ChangeLog

### Fixes
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

### Fixes
* Fixed the bug that identity acquisition failed when switching navigation

---

<!-- 2022-09-08 -->
# V1.8.16 ChangeLog

### Optimization Updates
* Optimize the display of expiration time

### Fixes
* Fixed the bug that identity acquisition failed when switching navigation

---

<!-- 2022-09-02 -->
# V1.8.15 ChangeLog

### Fixes
* healthz modifies the celery check timeout
* Fix the bug that the role has only one role and is a system administrator

---

<!-- 2022-09-01 -->
# V1.8.14 ChangeLog

### Fixes
* healthz relies on user management logic optimization
* Fix the bug that the role is only the system administrator page

### Optimization Updates
* The minimum length of user group names is updated to 2 characters

---

<!-- 2022-08-25 -->
# V1.8.13 ChangeLog

### Fixes
* No permission to jump to apply for recommendation permission to remove the user's existing permission
* Update management class api error information
* Multi-window page switching hierarchical administrator permission problem

---

<!-- 2022-08-04 -->
# V1.8.12 ChangeLog

### Fixes
* Modify the header jump logic
* Rating admin delete user group error

---

<!-- 2022-07-28 -->
# V1.8.11 ChangeLog

### Optimization Updates
* Listen to ipv6

### Fixes
* Modifying the basic information of the grading manager only checks the limit on the number of new members

---

<!-- 2022-07-19 -->
# V1.8.10 ChangeLog

### Fixes
* Fix model_event change event fails to execute due to data conversion error

---

<!-- 2022-07-12 -->
# V1.8.9 ChangeLog

### Features
* Added grading administrator guidelines

---

<!-- 2022-07-01 -->
# V1.8.8 ChangeLog

### Fixes
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

### Fixes
* Fixed the issue that the newly created associated instance authorization API whitelist-monitoring whitelist does not take effect

---

<!-- 2022-06-16 -->
# V1.8.5 ChangeLog

### Fixes
* Fix the problem that the recommended action cannot be selected by clicking

---

<!-- 2022-05-31 -->
# V1.8.4 ChangeLog

### Features
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

### Fixes
* Fix front-end related experience issues

---

<!-- 2022-05-16 -->
# V1.8.3 ChangeLog

### Fixes
* When only temporary permissions, my permissions do not show problems
* Temporary permission expiration time selection problem
* request_id parameter error problem

---

<!-- 2022-05-13 -->
# V1.8.2 ChangeLog

### Fixes
* Temporary permissions system switching operation is not clear
* Temporary permissions Polymerization Operation Resources Selection Problems

---

<!-- 2022-05-10 -->
# V1.8.1 ChangeLog

### Features
* jump without permission to increase recommendation permission

---

<!-- 2022-03-23 -->
# V1.8.0 ChangeLog

### Features
* temporary permission

---

<!-- 2022-05-19 -->
# V1.7.19 ChangeLog

### Fixes
* Unauthorized jump application has no dependent operation problem

---

<!-- 2022-05-12 -->
# V1.7.18 ChangeLog

### Fixes
* Resource instance selection subordinate search error problem

---

<!-- 2022-04-26 -->
# V1.7.17 ChangeLog

### Fixes
* Fixed Aggregate operation unlimited problem

---

<!-- 2022-04-25 -->
# V1.7.16 ChangeLog

### Fixes
* Fixed Aggregate operation batch copy batch paste

---

<!-- 2022-04-25 -->
# V1.7.15 ChangeLog

### Fixes
* Fixed issues related to selection of aggregation operations
* Approval process operation list supports internationalization

### Optimization Updates
* Django version upgraded to 2.2.27

---

<!-- 2022-04-21 -->
# V1.7.14 ChangeLog

### Features
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

### Fixes
* Fixed internationalization related data

### Optimization Updates
* Navigation bar display

---

<!-- 2022-04-07 -->
# V1.7.11 ChangeLog

### Fixes
* Fixed the ITSM display problem of the application form for grading administrators
* Fix front-end merge selection instance problem

### Optimization Updates
* sentry sdk switch

---

<!-- 2022-04-01 -->
# V1.7.10 ChangeLog

### Fixes
* Querying a subject with permission to fix a cross-system resource query error

---

<!-- 2022-04-01 -->
# V1.7.9 ChangeLog

### Fixes
* Fix the error of resource permission management query interface
* Fixed the problem that when adding multiple group permissions to a user group across pages, the permission template selected across the pages would be missing after confirmation.
* Fixed an issue where the application has associated permissions, and the default period will become unchangeable after selecting an instance

---

<!-- 2022-03-24 -->
# V1.7.8 ChangeLog

### Fixes
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

### Fixes
* Fixed issues related to front-end user group configuration permissions
* Synchronized the organizational structure department and fixed the data error problem of department lft/rght/level

---

<!-- 2022-03-02 -->
# V1.7.4 ChangeLog

### Fixes
* Fix the problem of redis connection leak caused by healthz
* Fixed the problem that the front-end user group configuration permissions did not display the resource type

---

<!-- 2022-02-24 -->
# V1.7.3 ChangeLog

### Fixes
* Fix automatic registration apigateway configuration error

---

<!-- 2022-02-24 -->
# V1.7.2 ChangeLog

### Fixes
* Fix permission template change operation error
* Fix automatic registration apigateway configuration error

---

<!-- 2022-02-21 -->
# V1.7.1 ChangeLog

### Features
* Regularly clean up unquoted expressions in the background

### Optimization Updates
* Optimize operation audit information
* Optimize log printing
* Optimize SaaS Django configuration, remove blueapps dependency

---

<!-- 2022-01-20 -->
# V1.6.5 ChangeLog

### Fixes
* Fix apigateway register settings error

### Optimization Updates
* ESB and Login slow http request log to component.log
* add creator_authorization_instance white list: bk_job/file_resource

---

<!-- 2021-12-23 -->
# V1.6.4 ChangeLog

### Fixes
* Fix the permission transfer bug
* Fix the script error of automatic registration apigateway
* Fixed an error in the status of the synchronization ITSM application form

---

<!-- 2021-12-21 -->
# V1.6.3 ChangeLog

### Features
* query authorized subjects

---

<!-- 2021-12-16 -->
# V1.6.2 ChangeLog

### Features
* opentelemetry tracing

### Optimization Updates
* add permission handover switch

---

<!-- 2021-12-10 -->
# V1.6.1 ChangeLog

### Features
* Permission transfer

### Optimization Updates
* Front-end refactoring

---

<!-- 2021-12-08 -->
# V1.5.16 ChangeLog

### Optimization Updates
* Do not delete back-end users and departments when the organizational structure is synchronized

### Fixes
* Lock the dependency package typing-extensions version to avoid deployment failure caused by automatic update to the latest version

---

<!-- 2021-12-06 -->
# V1.5.15 ChangeLog

### Fixes
* Fixed the issue that celery_id was obtained as None after LongTask changed synchronization
* Fixed the issue of incompatible action_id with the Scope data structure of the hierarchical administrator authority

---

<!-- 2021-11-30 -->
# V1.5.14 ChangeLog

### Features
* Support apigateway init with apis and docs

### Optimization Updates
* Automatically update the resource instance name to ignore the defensiveness of the big strategy
* Added bk_nocode whitelist for accessing system management API
* Support to return exception information when calling a third-party interface fails
* User group authorization is adjusted to execute tasks immediately

### Fixes
* Automatically update the resource instance name to be compatible with the access system callback exception
* Solve the authorization exception when the resource instance view is empty

---

<!-- 2021-11-23 -->
# V1.5.13 ChangeLog

### Features
* Authorized API whitelist supports prefix matching rules
* Automatically update the renamed resource instance in the strategy

### Optimization Updates
* Organization name tips show the full path
* Add line breaks to the log details in the synchronization record of the organizational structure
* The access system management API supports the authorization of unlimited resource instances for the creation of hierarchical administrators and user group authorization interfaces

### Fixes
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

### Fixes
* Fix the log configuration of the containerized version
* Fix redis timeout configuration problem

---

<!-- 2021-10-20 -->
# V1.5.10 ChangeLog

### Fixes
* Fix the issue of unauthorized access to the user group member list

---

<!-- 2021-10-20 -->
# V1.5.9 ChangeLog

### Fixes
* Fix long task get results error

---

<!-- 2021-10-20 -->
# V1.5.8 ChangeLog

### Optimization Updates
* Optimize resource callback structure error prompt
* Long-term task retry

### Fixes
* Fix the issue that the updated template is not synchronized to the user group permissions
* Fixed the problem of cookie domain error when port is not 80/443
* Uncheck the corresponding permission instance and report an error
* Fix the bug of tag return value when linking data in the background

---

<!-- 2021-10-11 -->
# V1.5.7 ChangeLog

### Fixes
* Fix the problem of multiple url splicing/causing access errors
* Fix the problem of the wrong address of the front-end personnel list component range

---

<!-- 2021-10-11 -->
# V1.5.6 ChangeLog

### Fixes
* Repair management API-user group custom authorization asynchronously causes continuous authorization failure

---

<!-- 2021-10-08 -->
# V1.5.5 ChangeLog

### Fixes
* User group update template authorization error

---

<!-- 2021-09-29 -->
# V1.5.4 ChangeLog

### Optimization Updates
* Custom permission application supports instance approvers
* The jump application does not merge the user's existing permissions
* The number of instances of the authorization api return strategy

### Fixes
* Fixed the display problem of the renewal email link in the corporate WeChat email
* My permission user group permission check status prompt delete bug
* The business jump permission center applies for permission, the application period cannot be modified
* Fix the display problem of general operation

---

<!-- 2021-09-24 -->
# V1.5.3 ChangeLog

### Fixes
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

### Fixes
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

### Fixes
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

### Fixes
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

### Fixes
* User group authorization verification rating manager authorization scope error problem
* Ignoring the path on the authorization page causes the authorization data error problem

---

<!-- 2021-08-11 -->
# V1.4.28 ChangeLog

### Optimization Updates
* Optimized "Ignore Path" to display the full path on the front end

### Fixes
* Fix the error of specific host instances authorized by the operating platform

---

<!-- 2021-08-10 -->
# V1.4.27 ChangeLog

### Optimization Updates
* Optimize resource type ID verification
* Optimize operation ID verification
* Optimize the saving of resource types

### Fixes
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

### Fixes
* Fix the issue of adding gsekit permission error
* Fix the difference contrast exception

---

<!-- 2021-08-02 -->
# V1.4.25 ChangeLog

### Fixes
* The application form details are rejected for non-applicants to view
* The operation list refuses to be viewed by non-login users

---

<!-- 2021-08-02 -->
# V1.4.24 ChangeLog

### Optimization Updates
* Renewal page interaction optimization

### Fixes
* Fix V2migrate api permission template adds authorization object error bug
* Fix the problem of ignoring the failure of path authorization instance
* Fix the problem that the custom permission application clicks to renew and does not respond

---

<!-- 2021-07-22 -->
# V1.4.23 ChangeLog

### Optimization Updates
* Remove the "permanent" time from the validity period on the application side
* Some known issues have been optimized

### Fixes
* Fix the problem that the expiration time of the automatic filling of dependent operations is empty
* Fixed the problem that the hierarchical administrator failed to save the range of personnel selected
* Fix the issue that the dependent operation instance becomes read-only
* Fix some known issues

---

<!-- 2021-07-20 -->
# V1.4.22 ChangeLog

### Fixes
* Fix the issue that the expiration time of the related action is empty

---

<!-- 2021-07-20 -->
# V1.4.21 ChangeLog

### Fixes
* Fix the security issue of any Origin request in CORS
* Fixed an error on the edit level administrator page
* Fix the problem of editing user group permissions, adding custom permissions is not saved, editing custom permissions again, and adding custom permissions after saving is not displayed on the permissions page
* Fixed the problem that after applying for custom permissions and selecting associated permissions, the post-privileges select the instance, and the pre-privilege instance period is empty and cannot be modified

---

<!-- 2021-07-19 -->
# V1.4.20 ChangeLog

### Fixes
* Fix the problem that the custom permission application cannot be edited after selecting the resource instance when there is a dependency
* Fix the issue that the validity period of custom permissions is empty

---

<!-- 2021-07-15 -->
# V1.4.19 ChangeLog

### Features
* Hierarchical administrator related operation links support role id parameters; support automatic switching of hierarchical administrator status

### Optimization Updates
* My permission, when there is only one system custom permission, expand by default
* Update the whitelist of ITSM new association API

### Fixes
* Fix the operation problem of deleting hierarchical administrators
* Fix the problem of adding custom permissions and template permissions to the group at the same time
* Fix the display problem of recommended permissions for hierarchical administrators
* Fix the problem caused when the staff input box has spaces

---

<!-- 2021-07-13 -->
# V1.4.18 ChangeLog

### Optimization Updates
* Hierarchical administrator edit mode optimization

### Fixes
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

### Fixes
* Fix the problem that the user group add template permission selection instance style is disorderly
* Fix the problem that the select box of some instances is not clickable when adding user group permissions
* Fix the optimization of the edit mode of the hierarchical administrator, and the maximum permission range is collapsed by default
* Fix the issue that "editing" is still displayed after the permission template is updated

---

<!-- 2021-07-05 -->
# V1.4.16 ChangeLog

### Fixes
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

### Features
* Supports asynchronous delete action and delete action strategy
* User group custom permissions support deleting a certain operation permission function
* Support the function of enabling system access through environment variables

### Optimization Updates
* Optimized editing of user group permissions
* Optimized editing of user group permissions
* The authorized user group OpenAPI supports skipping the verification of the authority scope of the hierarchical administrator

### Fixes
* Fix the copywriting problem
* Fix the problem of automatic expansion of selected instances in batch editing (merge selection)

---

<!-- 2021-06-17 -->
# V1.4.12 ChangeLog

### Features
* The SaaS side does not have permission to jump to automatically match the user group

### Optimization Updates
* Hierarchical administrator switch identity optimization

### Fixes
* Fix the ID search bug on the application user group page
* Fix the caching problem of search conditions on the application page
* Fix the problem of failure to exit the hierarchical administrator

---

<!-- 2021-06-15 -->
# V1.4.11 ChangeLog

### Features
* New administrator API-get a user group list under a certain hierarchical administrator
* Support user group authorization API

### Fixes
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

### Fixes
* Fix the problem that the SaaS introduced in 1.4.5 deletes the user group, but it is not deleted in the background, which causes the permission error

---

<!-- 2021-05-19 -->
# V1.4.8 ChangeLog

### Features
* Authorize Open API to support validity period setting
* Batch authorization Open API supports granting unlimited permissions
* Support delete policy subscription event push

### Optimization Updates
* Open API supports error code 1902409 to indicate conflicts of duplicate names, etc.
* My permission page sort adjustment

### Fixes
* Fix the problem of lack of full range judgment when filtering user groups
* Fix the problem that the member of the hierarchical administrator cannot be deleted
* Fix the duplicate display problem of Tips for permission resource instances

---

<!-- 2021-05-13 -->
# V1.4.7 ChangeLog

### Features
* Automatically generate aggregation action configuration
* Dependent action
* User groups support filtering by role
* ping api

---

<!-- 2021-04-28 -->
# V1.4.6 ChangeLog

### Features
* Management API-Creating hierarchical administrator and user group authorization support granting unlimited access to some resources
* Management APIs support configuration of the scope of systems that can be controlled and authorized by the system

---

<!-- 2021-04-27 -->
# V1.4.5 ChangeLog

### Optimization Updates
* My Permissions page optimization

### Fixes
* Fix the problem that the number of members of its associated authority template is not updated when the user group is deleted
* Fix the problem that the name can be empty when updating the permission template
* Fix the user group authorization when the new permission template 404
* Fix the problem of reporting an error when adding a new user group with empty group permission

---

<!-- 2021-04-19 -->
# V1.4.4 ChangeLog

### Features
* New version of permission template
* User Group Custom Permissions

### Optimization Updates
* Optimization of some known issues

### Fixes
* Some known issues fixed

---

<!-- 2021-04-01 -->
# V1.3.6 ChangeLog

### Features
* New permission template full synchronization script

### Fixes
* Fix the issue of unverified instance selections created by grade manager

---

<!-- 2021-03-25 -->
# V1.3.5 ChangeLog

### Features
* Added GSEKIT action aggregation configuration

---

<!-- 2021-03-23 -->
# V1.3.4 ChangeLog

### Fixes
* Fix the issue that the hierarchical administrator limit does not take effect
* Fix the issue of invalid instance emptying when applying for permission

---

<!-- 2021-03-18 -->
# V1.3.3 ChangeLog

### Optimization Updates
* Advance de-duplication when adding users to user groups
* Select Action Panel to de-expand for more interactions

### Fixes
* Fix the problem of overstepping the authority when updating the basic information of graded administrators
* Fix the copy-paste error problem when selecting unlimited instances
* Fix the audit error problem caused by v2migrate api authentication
* Fix the cryptographic interpreter logging celery task trace information error reporting problem

---

<!-- 2021-03-09 -->
# V1.3.2 ChangeLog

### Features
* Grading administrator adds cloning function

### Code Optimization
* Partial code refactoring

### Optimization Updates
* Add a quick selection of operation groups when the grading administrator selects the operation

### Fixes
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

### Features
* Support Debug Trace based on Request ID or task ID

### Optimization Updates
* Add a limit of 1000 for the maximum number of user group members

---

<!-- 2021-02-19 -->
# V1.2.15 ChangeLog

### Fixes
* Fix BK_PAAS_HOST with port can not verify through CSRF_TRUSTED_ORIGINS
* Fix the problem of over-limiting the user group of renewal reminder email for graded administrators

---

<!-- 2021-02-02 -->
# V1.2.14 ChangeLog

### Fixes
* Fix the problem that the operation name is not displayed in the ITSM approval document when the custom authority is renewed

---

<!-- 2021-01-28 -->
# V1.2.13 ChangeLog

### Features
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

### Fixes
* Fix the problem of hierarchy selection during permission configuration
* Fix the problem of incorrect display of the validity period of application documents

---

<!-- 2021-01-20 -->
# V1.2.11 ChangeLog

### Fixes
* Fix the application of updating rating manager exception
* Fix common operation selection grouping exception

---

<!-- 2021-01-15 -->
# V1.2.10 ChangeLog

### Fixes
* Fix the update rating manager exception

---

<!-- 2021-01-14 -->
# V1.2.9 ChangeLog

### Features
* Instance authorization-related APIs add whitelist restrictions
* Internationalized time zone support

### Optimization Updates
* Edit templates and hierarchical administrators to add resource instance IDs and Name checks
* Side sliding closure adds secondary confirmation interaction
* Added permissions do not determine whether they are expired or not
* Enum class code refactoring optimization
* Celery Healthz Optimization

### Fixes
* Fixed the problem that users do not have abnormalities when the authentication-related interface judges super privileges
* Fixed the problem of wrong display of table data when merging operations when creating a new permission template

---

<!-- 2021-01-14 -->
# V1.2.8 ChangeLog

### Fixes
* Fix the problem of migration failure caused by user group not binding hierarchical administrator when migrating V2 data to V3

---

<!-- 2020-12-31 -->
# V1.2.7 ChangeLog

### Features
* Customized application to add operation grouping function

### Optimization Updates
* Sync admin user and add as super admin member when default Migrate DB
* Feedback links support multiple version differentiation
* No permission to jump to locate the selected operation
* Topology instances support batch selection by pressing and holding shift

### Fixes
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

### Features
* Add newbie guide
* Add policy expiration email reminder

### Optimization Updates
* Optimize authorization without updating if the existing policy contains a new policy
* Add default group non-deletion logic for operation groups

### Fixes
* Fix the DB contention lock issue that may occur when deleting policy instances
* Fix the error when choosing a specific instance for permission template aggregation instance
* Fix the sidebar that triggers the opening of the selected instance when you click Batch Paste for the selected instance

---

<!-- 2020-12-17 -->
# V1.2.5 ChangeLog

### Features
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

### Fixes
* Repair the error in displaying the switch status of aggregation operation when editing the hierarchical administrator
* Repair the setting of default approval process data does not take effect in time

### Package Dependencies
* [ee] bk_itsm >= 2.5.7.235 ([ce] bk_itsm >= 2.5.7.237)

---

<!-- 2020-12-03 -->
# V1.2.4 ChangeLog

### Features
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

### Fixes
* Fix search topology instance cache error
* Hierarchical Administrator Details Member List Edit Button Style Fixes
* Fix the problem of instance data mismatch when switching between unused views when there is a range limitation in multiple instance views in the new permission template
* New Permission Template Property Selection Box Disable Problem when Super Admin
* New hierarchical administrator selected to fix instance data error when saving the same operation id across systems

---

<!-- 2020-11-26 -->
# V1.2.3 ChangeLog

### Features
* Hierarchical administrator applies for modification

### Optimization Updates
* Create hierarchical administrators to support generating dependent operations

### Fixes
* Permission template modified some resources but not deleted bug
* Several front-end bug fixes

---

<!-- 2020-11-20 -->
# V1.2.2 ChangeLog

### Features
* Support the addition of new users in real time within 1 minute

### Optimization Updates
* Initialised Super Admin approach adjusted from API calls to Migrate DB on deployment
* The individual instances are displayed directly when applying for permission to select them
* Product documentation link updates
* New permission template Search should be adjusted to front-end search when restricted data exists for the instance
* Login window resizing

### Fixes
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

### Fixes
* Fix open api role auth error where super manager not exists
* Fixed the bug that the copy instance paste button is displayed when requesting permissions.

---

<!-- 2020-11-17 -->
# V1.2.0 ChangeLog

### Features
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

### Fixes
* Fix search topology instance cache error

---

<!-- 2020-11-12 -->
# V1.1.45 ChangeLog

### Features
* User logout support

### Optimization Updates
* Update product documentation links

### Fixes
* Repair the problem of empty description when switching system with new permission template.
* Repair the problem of saving exception when editing basic information of user group.

---

<!-- 2020-11-09 -->
# V1.1.44 ChangeLog

### Fixes
* Fix the error of adding unlimited front-end processing instance selection.

---

<!-- 2020-11-04 -->
# V1.1.43 ChangeLog

### Features
* New product documentation link entry

### Optimization Updates
* Resource instance search first level error message optimization
* Table search box front-end optimization

---

<!-- 2020-10-22 -->
# V1.1.42 ChangeLog

### Fixes
* Fix the add tag problem of data migration interface

---

<!-- 2020-10-20 -->
# V1.1.41 ChangeLog

### Fixes
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

### Features
* Support for search of topological instances

### Optimization Updates
* Synchronized Organizational Architecture Distributed Lock Failure Prompt Failure and Logging

### Fixes
* Fix the problem of incomplete pull due to sorting problem when synchronizing organizational structure pagination to get departments and users.

---

<!-- 2020-09-25 -->
# V1.1.37 ChangeLog

### Optimization Updates
* Exceptional error messages and log optimizations for interfaces related to resource queries for access to the system

### Fixes
* Repair the problem that the authorization of new related properties does not take effect.

---

<!-- 2020-09-23 -->
# V1.1.36 ChangeLog

### Features
* Support the ability to paste resource instances

### Optimization Updates
* Topology instance selection panel supports dragging
* No drop-down list is needed when there is only one instance view.

### Fixes
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

## BKIAM-V3 V1.1.0 goes online !

### Feature

* [ feature ] `Apply` According to user scenarios, we support to apply by permission templates, join  groups, and
 customize application:

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
