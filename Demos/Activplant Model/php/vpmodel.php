<?php
$config = include('config.php');

$assetCount = 0;
$groupCount = 0;

$nodeGroups = array();  //Flat list
$nodeHierarchy = array();   //Build recursively

class NodeModel
{
    public $databaseName;
    public $assetCount;
    public $groupCount;
    public $equipmentModel = array();
}

class NodeGroup
{
    public $groupId;
    public $type = "NodeGroup";
    public $groupName;
    public $parentId;
    //public $groupParentName;  //for debugging
    public $groupDescription;
    public $groupChildren = array();
}

class Node
{
    public $nodeId;
    public $type = "Node";
    public $nodeName;
    public $parentId;
    public $nodeCode;
    public $nodeDescription;
    //public $nodeState;    //TODO
    //public $nodeAttributes = array(); //TODO
}

function OpenDBConnection($config) {
    $serverName = "tcp:" . $config['dbserver'];
    $connectionOptions = array(
            "Database"=>$config["dbname"],
            "Uid"=>$config["dbuser"], 
            "PWD"=>$config["dbpassword"]
    );
    $conn = sqlsrv_connect($serverName, $connectionOptions);
    if($conn == false)
        die(FormatErrors(sqlsrv_errors()));

    return $conn;
}

function LoadNodeGroups($config) {
    $nodeGroups = array();
    try
    {
        $conn = OpenDBConnection($config);
        $tsql = "SELECT * FROM [ActivplantDB02_rest].[dbo].[tblOS_Groups] ORDER BY GroupID";
        $getNodeGroups = sqlsrv_query($conn, $tsql);
        if ($getNodeGroups == FALSE)
            die(FormatErrors(sqlsrv_errors()));
        while($row = sqlsrv_fetch_array($getNodeGroups, SQLSRV_FETCH_ASSOC))
        {
            $newNodeGroup = new NodeGroup();
            $newNodeGroup->groupId = $row['GroupID'];
            $newNodeGroup->parentId = $row['ParentGroupID'];
            $newNodeGroup->groupName = $row['GroupName'];
            $newNodeGroup->groupDescription = $row['Description'];

            if (!array_key_exists($row['GroupID'], $nodeGroups)) {
                $nodeGroups[$row['GroupID']] = $newNodeGroup;
                $GLOBALS["groupCount"]++;
            }
        }
        sqlsrv_free_stmt($getNodeGroups);
        sqlsrv_close($conn);
    }
    catch(Exception $e)
    {
        echo("Error!");
    }
    return $nodeGroups;
}

function LoadNodesForGroup($config, $parentGroupId) {
    $nodesForGroup = array();
    try
    {
        $conn = OpenDBConnection($config);
        $tsql = "SELECT * FROM [ActivplantDB02_rest].[dbo].[tblOS_Nodes] WHERE NodeGroupID = " . $parentGroupId;
        $getNodes = sqlsrv_query($conn, $tsql);
        if ($getNodes == FALSE)
            die(FormatErrors(sqlsrv_errors()));
        while($row = sqlsrv_fetch_array($getNodes, SQLSRV_FETCH_ASSOC))
        {
            $newNode = new Node();
            $newNode->nodeId = $row['NodeID'];
            $newNode->parentId = $parentGroupId;
            $newNode->nodeName = $row['NodeName'];
            $newNode->nodeCode = $row['NodeCode'];
            $newNode->nodeDescription = $row['Description'];

            if (!array_key_exists($row['NodeID'], $nodesForGroup)) {
                $nodesForGroup[$row['NodeID']] = $newNode;
            }
        }
        sqlsrv_free_stmt($getNodes);
        sqlsrv_close($conn);
    }
    catch(Exception $e)
    {
        echo("Error!");
    }
    return $nodesForGroup;
}


//First load flat list
$nodeGroups = LoadNodeGroups($config);

//Build group hiearchy recursively
foreach ($nodeGroups as $key => $group) {
    //If a parent node was found, add this to it
    $found = AppendGroupToGroupParent($config, $group->parentId, $group, $nodeHierarchy, false);
    //If not, this must be the root node, create it
    if (!$found) {
        //$group->groupParentName = "Root Node";    //for debugging
        $nodeHierarchy[$key] = $group;
    }
}
function AppendGroupToGroupParent($config, $parentId, $group, $nodeHierarchy, $found) {
    foreach ($nodeHierarchy as $key => $nodeGroup) {
        if ($nodeGroup->groupId == $parentId) {
            //$group->groupParentName = $nodeGroup->groupName;  //for debugging
            $nodeHierarchy[$key]->groupChildren[$group->groupId] = $group;
            return true;
        } else {
            $found = AppendGroupToGroupParent($config, $parentId, $group, $nodeGroup->groupChildren, $found);
        }
    }
    return $found;
}

//Load assets for each group recursively
foreach ($nodeHierarchy as $key => $branch) {
    AppendAssetsToGroups($config, $branch);
}
function AppendAssetsToGroups($config, $branch) {
    
    //If this group has child groups, follow them recursively
    if (count($branch->groupChildren) > 0) {  
        foreach ($branch->groupChildren as $key => $childGroup) {
            if ($childGroup->type == "NodeGroup") {
                AppendAssetsToGroups($config, $childGroup);
            }
        }
    }
    //Add any assets that are immediate children of this group
    $childAssets = LoadNodesForGroup($config, $branch->groupId);
    if (isset($childAssets)) {
        foreach ($childAssets as $key => $childAsset) {
            $branch->groupChildren[$key] = $childAsset;
            $GLOBALS["assetCount"]++;
        }
    }
    return $branch;
}

# Output built model
header("Content-Type: application/json");
$model = new NodeModel();
$model->databaseName = $config["dbname"];
$model->assetCount = $GLOBALS["assetCount"];
$model->groupCount = $GLOBALS["groupCount"];
$model->equipmentModel = $nodeHierarchy;
echo(json_encode($model));
?>